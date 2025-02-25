import os
import ffmpeg
import soundfile as sf
import librosa
import numpy as np
import string

def is_none_or_whitespace(text: str) -> bool:
    return text == None or text.strip() == ""

def normalize_text(text: str):
    normalized_text = text.translate(str.maketrans('', '', string.punctuation)).lower().strip()
    return normalized_text

def load_filtered_phrases(filter_list_path: str) -> list[str]:
    filtered_phrases = list()
    with open(filter_list_path) as file:
        for line in file:
            normalized_line = normalize_text(line)
            if not is_none_or_whitespace(normalized_line):
                filtered_phrases.append(normalized_line)
    return filtered_phrases

def load_audio(audio_file: str) -> tuple[np.ndarray, int]:
    audio_data, sr = librosa.load(audio_file, sr=None)
    return audio_data, sr

def save_audio(audio: np.ndarray, sr: int, save_path: str):
    path = os.path.dirname(save_path)
    if not is_none_or_whitespace(path):
        os.makedirs(path, exist_ok=True)
    
    sf.write(save_path, audio, sr)

def extract_audio_from_video(video_file: str, output_file: str):
    ffmpeg.input(video_file).output(output_file).run(overwrite_output=True, quiet=True)

def combine_audio_video_files(video_file: str, audio_file: str, output_file: str):
    video = ffmpeg.input(video_file)
    audio = ffmpeg.input(audio_file)
    ffmpeg.concat(video, audio, v=1, a=1).output(output_file).run(overwrite_output=True, quiet=True)