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

def load_audio(audio_file: str, target_sr: int = None) -> tuple[np.ndarray, int, str]:
    audio_data, sr = sf.read(audio_file, always_2d=True)

    #resample if needed
    if target_sr is not None and sr != target_sr:
        audio_data = librosa.resample(y=audio_data, orig_sr=sr, target_sr=target_sr, axis=0)
        sr = target_sr

    if audio_data.ndim < 2:
        audio_data = audio_data.reshape(-1, 1)

    subtype = None
    with sf.SoundFile(audio_file) as f:
        subtype = f.subtype

    return audio_data, sr, subtype

def convert_stereo_to_mono(waveform: np.ndarray):
    mono_waveform = np.copy(waveform)
    if mono_waveform.ndim > 1 and mono_waveform.shape[1] > 1:
        mono_waveform = np.mean(waveform, axis=1)
    return mono_waveform

def trim_silence(array: np.ndarray, silence_threshold: int = 0.01, required_silence_length: int = 100) -> np.ndarray:
    concurrent_silence = 0
    mask = np.full(array.shape[0], True, dtype=bool)
    for i in range(0, array.shape[0]):
        volume = np.sum(array[i, :])/2
        concurrent_silence = concurrent_silence + 1 if volume < silence_threshold else 0
        if concurrent_silence >= required_silence_length:
            mask[i] = False

    filtered_array = array[mask]
    return filtered_array

def create_folders(full_path: str):
    path = os.path.dirname(full_path)
    if not is_none_or_whitespace(path):
        os.makedirs(path, exist_ok=True)

def save_audio(audio: np.ndarray, sr: int, save_path: str, subtype: str="PCM_16"):
    create_folders(save_path)
    sf.write(save_path, audio, sr, subtype=subtype)

def extract_audio_from_video(video_file: str, output_file: str):
    ffmpeg.input(video_file).output(output_file).run(overwrite_output=True, quiet=True)

def combine_audio_video_files(video_file: str, audio_file: str, output_file: str, audio_bitrate: str=None):
    video = ffmpeg.input(video_file)
    audio = ffmpeg.input(audio_file)

    if audio_bitrate:
        ffmpeg.output(video['v'], audio['a'], output_file, vcodec='copy', audio_bitrate=audio_bitrate).run(overwrite_output=True, quiet=True)
    else:
        ffmpeg.output(video['v'], audio['a'], output_file, vcodec='copy').run(overwrite_output=True, quiet=True)

def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)