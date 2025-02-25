FROM python:3.11.4-slim-buster
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -c "import whisper; whisper.load_model('small.en')"
RUN python -c "import torchaudio; pipeline = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H; model = pipeline.get_model()"
ENTRYPOINT ["python", "run.py"]
