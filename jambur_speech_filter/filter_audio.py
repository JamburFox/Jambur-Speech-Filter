import numpy as np
import torch

from .whisper import WhisperModel
from .aligner import JamburAligner
from .utils import load_audio, save_audio, normalize_text

def mute_segment(array: np.ndarray, sr: float, start: float, end: float) -> np.ndarray:
    start_filter_index = int(start * sr)
    end_filter_index = int(end * sr)
    array[start_filter_index:end_filter_index] = 0
    return array

def censor_all_phrases(audio_array: np.ndarray, sr: int, alignments: list[dict], filtered_phrases: list[str]) -> np.ndarray:
    modified_audio_data = np.copy(audio_array)

    for alignment in alignments:
        if normalize_text(alignment['word']) in filtered_phrases:
            start_filter_index = float(alignment['start'])
            end_filter_index = float(alignment['end'])
            mute_segment(modified_audio_data, sr, start_filter_index, end_filter_index)

    return modified_audio_data

def filter_audio(filtered_phrases: list[str], audio_file: str, audio_output_file: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    whisperModel = WhisperModel(device)
    aligner = JamburAligner(device)

    audio_data, sr = load_audio(audio_file)

    transcription = whisperModel.transcribe_audio(audio_file)
    alignments = aligner.align(transcription, audio_data.reshape(1, -1), sr)

    modified_audio_array = censor_all_phrases(audio_data, sr, alignments, filtered_phrases)

    save_audio(modified_audio_array, sr, audio_output_file)