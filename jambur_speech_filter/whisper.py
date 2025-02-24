import whisper
import torch

class WhisperModel():
    def __init__(self, device: str = "cuda") -> None:
        self.model = whisper.load_model("small.en").to(device)#small.en, medium.en

    def transcribe_audio(self, audio_path) -> str:
        result = self.model.transcribe(audio_path)
        return result['text']