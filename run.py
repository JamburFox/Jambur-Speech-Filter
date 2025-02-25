import argparse
import os
import sys
import shutil
import platform

from jambur_speech_filter.filter_audio import filter_audio
from jambur_speech_filter.utils import combine_audio_video_files, load_filtered_phrases, extract_audio_from_video

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the speaker id model.')
    parser.add_argument('--media_file', type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.wav"), help='the source media file')
    parser.add_argument('--output_file', type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_modified.wav"), help='the source media file')
    args = parser.parse_args()

    TEMP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    TEMP_AUDIO_FILE = os.path.join(TEMP_PATH, 'temp.wav')
    FILTER_LIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'filters', 'filtered_phrases.txt')
    LOCAL_FFMPEG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg', 'bin')
    SYSTEM = platform.system().lower()#windows, linux or darwin (mac)

    if not is_ffmpeg_in_path():
        if "windows" in SYSTEM:
            print("FFmpeg is not found in path! Updating Path to use local FFmpeg")
            os.environ["PATH"] = LOCAL_FFMPEG_PATH + os.pathsep + os.environ['PATH']
        else:
            print("local FFmpeg package does not support this OS, please install FFmpeg on your system!")

    filtered_phrases = load_filtered_phrases(FILTER_LIST_PATH)

    if file_is_video(args.media_file) and file_is_video(args.output_file):
        print("Filtering Video...")
        extract_audio_from_video(args.media_file, TEMP_AUDIO_FILE)
        filter_audio(filtered_phrases, TEMP_AUDIO_FILE, TEMP_AUDIO_FILE)

        print("Exporting Updated Video...")
        combine_audio_video_files(args.media_file, TEMP_AUDIO_FILE, args.output_file)

    elif file_is_audio(args.media_file) and file_is_audio(args.output_file):
        print("Filtering Audio...")
        filter_audio(filtered_phrases, args.media_file, args.output_file)

    else:
        print("File type not supported!")
        sys.exit(1)

    print("Done!")