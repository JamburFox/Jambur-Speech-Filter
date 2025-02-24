import torch
import torchaudio
import re
from dataclasses import dataclass
import numpy as np

@dataclass
class Point:
    token_index: int
    time_index: int
    score: float

@dataclass
class Segment:
    label: str
    start: int
    end: int
    score: float

    def __repr__(self):
        return f"{self.label}\t({self.score:4.2f}): [{self.start:5d}, {self.end:5d})"

    @property
    def length(self):
        return self.end - self.start

def convert_transcript(transcription: str) -> str:
    content = re.sub(r'[^a-zA-Z\s]', '', transcription)
    content = content.upper()
    words = content.split()
    result = '|' + '|'.join(words) + '|'
    return result

def load_audio_file(audio_file: str) -> tuple[torch.Tensor, int]:
    waveform, original_sample_rate = torchaudio.load(audio_file)
    return waveform, original_sample_rate

def get_trellis(emission: torch.Tensor, tokens: list[int], blank_id: int = 0) -> torch.Tensor:
    num_frame = emission.size(0)
    num_tokens = len(tokens)

    trellis = torch.zeros((num_frame, num_tokens))
    trellis[1:, 0] = torch.cumsum(emission[1:, blank_id], 0)
    trellis[0, 1:] = -float("inf")
    trellis[-num_tokens + 1 :, 0] = float("inf")

    for t in range(num_frame - 1):
        trellis[t + 1, 1:] = torch.maximum(
            trellis[t, 1:] + emission[t, blank_id],
            trellis[t, :-1] + emission[t, tokens[1:]],
        )
    return trellis

def backtrack(trellis: torch.Tensor, emission: torch.Tensor, tokens: list[int], blank_id: int = 0) -> list[Point]:
    t, j = trellis.size(0) - 1, trellis.size(1) - 1

    path = [Point(j, t, emission[t, blank_id].exp().item())]
    while j > 0:
        assert t > 0

        p_stay = emission[t - 1, blank_id]
        p_change = emission[t - 1, tokens[j]]

        stayed = trellis[t - 1, j] + p_stay
        changed = trellis[t - 1, j - 1] + p_change

        t -= 1
        if changed > stayed:
            j -= 1

        prob = (p_change if changed > stayed else p_stay).exp().item()
        path.append(Point(j, t, prob))

    while t > 0:
        prob = emission[t - 1, blank_id].exp().item()
        path.append(Point(j, t - 1, prob))
        t -= 1

    return path[::-1]

def merge_repeats(path: list[Point], transcription: str) -> list[Segment]:
    i1, i2 = 0, 0
    segments = []
    while i1 < len(path):
        while i2 < len(path) and path[i1].token_index == path[i2].token_index:
            i2 += 1
        score = sum(path[k].score for k in range(i1, i2)) / (i2 - i1)
        segments.append(
            Segment(
                transcription[path[i1].token_index],
                path[i1].time_index,
                path[i2 - 1].time_index + 1,
                score,
            )
        )
        i1 = i2
    return segments

def merge_words(segments: list[Segment], separator: str = "|") -> list[Segment]:
    words = []
    i1, i2 = 0, 0
    while i1 < len(segments):
        if i2 >= len(segments) or segments[i2].label == separator:
            if i1 != i2:
                segs = segments[i1:i2]
                word = "".join([seg.label for seg in segs])
                score = sum(seg.score * seg.length for seg in segs) / sum(seg.length for seg in segs)
                words.append(Segment(word, segments[i1].start, segments[i2 - 1].end, score))
            i1 = i2 + 1
            i2 = i1
        else:
            i2 += 1
    return words

class JamburAligner():
    def __init__(self, device: str = "cuda"):
        self.device = device
        self.target_sample_rate = 16000
        self.bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
        self.model = self.bundle.get_model().to(self.device)
        self.labels = self.bundle.get_labels()
        self.labels_dictionary = {c: i for i, c in enumerate(self.labels)}

    def tokenize_transcription(self, transcription: str) -> list[int]:
        tokens = [self.labels_dictionary[c] for c in transcription]
        return tokens

    def get_segment(self, segment: Segment, waveform: torch.Tensor, trellis: torch.Tensor) -> tuple[str, float, float]:
        ratio = waveform.size(1) / trellis.size(0)
        x0 = int(ratio * segment.start)
        x1 = int(ratio * segment.end)
        word_start = x0 / self.bundle.sample_rate
        word_end = x1 / self.bundle.sample_rate
        return segment.label, word_start, word_end

    def align(self, transcription: str, waveform: np.ndarray, sample_rate: int) -> list[dict]:
        converted_transcription = convert_transcript(transcription)
        
        with torch.inference_mode():
            if sample_rate != self.target_sample_rate:
                resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=self.target_sample_rate)
                waveform = resampler(torch.from_numpy(waveform))

            emissions, _ = self.model(waveform.to(self.device))
            emissions = torch.log_softmax(emissions, dim=-1)
        emission = emissions[0].cpu().detach()

        tokens = self.tokenize_transcription(converted_transcription)
        trellis = get_trellis(emission, tokens)
        path = backtrack(trellis, emission, tokens)
        segments = merge_repeats(path, converted_transcription)
        word_segments = merge_words(segments)

        word_alignments = []
        split_words = transcription.split()
        for i, word in enumerate(word_segments):
            word, start, end = self.get_segment(word, waveform, trellis)
            if i < len(split_words):
                word_alignments.append({"word": split_words[i], "start": start, "end": end})
            else:
                word_alignments.append({"word": word.lower(), "start": start, "end": end})
        return word_alignments