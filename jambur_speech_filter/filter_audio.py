import numpy as np
import torch

from .whisper import WhisperModel
from .aligner import JamburAligner
from .utils import load_audio, save_audio, normalize_text, convert_stereo_to_mono, trim_silence

def mute_segment(array: np.ndarray, sr: float, start: float, end: float) -> np.ndarray:
    start_filter_index = int(start * sr)
    end_filter_index = int(end * sr)
    array[start_filter_index:end_filter_index, :] = 0
    return array

def add_segment(array: np.ndarray, sr: float, add_array: np.ndarray, index: float) -> np.ndarray:
    start_add_index = int(index * sr)
    end_add_index = min(start_add_index + add_array.shape[0], array.shape[0])
    array[start_add_index:end_add_index, :] += add_array[:end_add_index - start_add_index, :]
    return array

def add_segment_centred(array: np.ndarray, sr: float, add_array: np.ndarray, start: float, end: float) -> np.ndarray:
    start_segment_index = int(start * sr)
    end_segment_index = int(end * sr)
    segment_length = end_segment_index-start_segment_index
    add_length = add_array.shape[0]
    diff = add_length-segment_length
    offset = diff//2

    start_offset = max(start_segment_index - offset, 0)
    end_offset = min(start_segment_index + add_length - offset, array.shape[0])

    array[start_offset:end_offset, :] += add_array[:end_offset - start_offset, :]
    return array

def censor_all_phrases(audio_array: np.ndarray, sr: int, alignments: list[dict], filtered_phrases: list[str]) -> np.ndarray:
    modified_audio_data = np.copy(audio_array)

    for alignment in alignments:
        if normalize_text(alignment['word']) in filtered_phrases:
            start_filter_index = float(alignment['start'])
            end_filter_index = float(alignment['end'])
            mute_segment(modified_audio_data, sr, start_filter_index, end_filter_index)

    return modified_audio_data

def filter_all_phrases(audio_array: np.ndarray, sr: int, filter_audio_array: np.ndarray, alignments: list[dict], filtered_phrases: list[str]) -> np.ndarray:
    modified_audio_data = np.copy(audio_array)

    for alignment in alignments:
        if normalize_text(alignment['word']) in filtered_phrases:
            start_filter_index = float(alignment['start'])
            end_filter_index = float(alignment['end'])
            mute_segment(modified_audio_data, sr, start_filter_index, end_filter_index)
            add_segment_centred(modified_audio_data, sr, filter_audio_array, start_filter_index, end_filter_index)

    return modified_audio_data

def filter_audio(filtered_phrases: list[str], audio_file: str, audio_output_file: str, filter_file: str = None, device: str = "cpu"):
    whisperModel = WhisperModel(device)
    aligner = JamburAligner(device)

    audio_data, sr, sub_type = load_audio(audio_file)
    transcription = whisperModel.transcribe_audio(audio_file)
    alignments = aligner.align(transcription, convert_stereo_to_mono(audio_data).reshape(1, -1).astype(np.float32), sr)

    if filter_file is not None:
        filter_audio_data, _, _ = load_audio(filter_file, sr)
        filter_audio_data = trim_silence(filter_audio_data)

        modified_audio_array = filter_all_phrases(audio_data, sr, filter_audio_data, alignments, filtered_phrases)
    else:
        modified_audio_array = censor_all_phrases(audio_data, sr, alignments, filtered_phrases)

    save_audio(modified_audio_array, sr, audio_output_file, sub_type)