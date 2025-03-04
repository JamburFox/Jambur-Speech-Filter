import argparse
import os
import sys
import shutil
import platform
import torch
import os

from jambur_speech_filter.filter_audio import filter_audio
from jambur_speech_filter.utils import combine_audio_video_files, load_filtered_phrases, extract_audio_from_video, delete_file, create_folders

TEMP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
TEMP_AUDIO_FILE = os.path.join(TEMP_PATH, 'temp.wav')
FILTER_LIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'filters', 'filtered_phrases.txt')
LOCAL_FFMPEG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg', 'bin')
SYSTEM = platform.system().lower()#windows, linux or darwin (mac)

def get_temp_path(filename: str):
    return os.path.join(TEMP_PATH, filename)

def is_ffmpeg_in_path():
    return shutil.which("ffmpeg") is not None

def file_is_video(filename: str):
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
    _, extension = os.path.splitext(filename)
    return extension.lower() in video_extensions

def file_is_audio(filename: str):
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
    _, extension = os.path.splitext(filename)
    return extension.lower() in audio_extensions

def create_temp_folder():
    print(f"Making Folders: {TEMP_AUDIO_FILE}")
    create_folders(TEMP_PATH)

def process_file(media_file: str, output_file: str, filter_file: str = None, audio_bitrate: str = "192k"):
    if not is_ffmpeg_in_path():
        if "windows" in SYSTEM:
            print("FFmpeg is not found in path! Updating Path to use local FFmpeg")
            os.environ["PATH"] = LOCAL_FFMPEG_PATH + os.pathsep + os.environ['PATH']
        else:
            print("local FFmpeg package does not support this OS, please install FFmpeg on your system!")

    filtered_phrases = load_filtered_phrases(FILTER_LIST_PATH)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    #load filter file

    if file_is_video(media_file) and file_is_video(output_file):
        print("Filtering Video...")
        extract_audio_from_video(media_file, TEMP_AUDIO_FILE)
        filter_audio(filtered_phrases, TEMP_AUDIO_FILE, TEMP_AUDIO_FILE, filter_file, device)

        print("Exporting Updated Video...")
        combine_audio_video_files(media_file, TEMP_AUDIO_FILE, output_file, audio_bitrate)

        #cleanup temp folder
        delete_file(TEMP_AUDIO_FILE)

        return output_file

    elif file_is_audio(media_file) and file_is_audio(output_file):
        print("Filtering and Exporting Audio...")
        filter_audio(filtered_phrases, media_file, output_file, filter_file, device)

        return output_file
    
    else:
        print("File type not supported!")

    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the speaker id model.')
    parser.add_argument('--media_file', type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.wav"), help='the source media file')
    parser.add_argument('--output_file', type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_modified.wav"), help='the filtered media file save location')
    parser.add_argument('--filter_file', type=str, default=None, help='the audio file to play over filtered segments')
    parser.add_argument('--audio_bitrate', type=str, default="192k", help='the output audio bitrate')
    args = parser.parse_args()

    create_temp_folder()
    file_out = process_file(media_file=args.media_file, output_file=args.output_file, filter_file=args.filter_file, audio_bitrate=args.audio_bitrate)
    if not file_out:
        sys.exit(1)

    print("Done!")
