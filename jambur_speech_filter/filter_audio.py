import numpy as np
import torch

from .whisper import WhisperModel
from .aligner import JamburAligner
from .utils import load_audio, save_audio, normalize_text, convert_stereo_to_mono

def mute_segment(array: np.ndarray, sr: float, start: float, end: float) -> np.ndarray:
    start_filter_index = int(start * sr)
    end_filter_index = int(end * sr)
    array[start_filter_index:end_filter_index, :] = 0
    return array

def censor_all_phrases(audio_array: np.ndarray, sr: int, alignments: list[dict], filtered_phrases: list[str]) -> np.ndarray:
    modified_audio_data = np.copy(audio_array)

    for alignment in alignments:
        if normalize_text(alignment['word']) in filtered_phrases:
            start_filter_index = float(alignment['start'])
            end_filter_index = float(alignment['end'])
            mute_segment(modified_audio_data, sr, start_filter_index, end_filter_index)

    return modified_audio_data

def filter_audio(filtered_phrases: list[str], audio_file: str, audio_output_file: str, device: str):
    whisperModel = WhisperModel(device)
    aligner = JamburAligner(device)

    audio_data, sr, sub_type = load_audio(audio_file)

    transcription = whisperModel.transcribe_audio(audio_file)
    alignments = aligner.align(transcription, convert_stereo_to_mono(audio_data).reshape(1, -1).astype(np.float32), sr)

    modified_audio_array = censor_all_phrases(audio_data, sr, alignments, filtered_phrases)

    save_audio(audio_data, sr, audio_output_file, sub_type)