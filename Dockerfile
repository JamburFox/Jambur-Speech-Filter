FROM python:3.11.4-slim-buster
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -c "import whisper; whisper.load_model('small.en')"
RUN python -c "import torchaudio; pipeline = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H; model = pipeline.get_model()"
#python is unable to create folders so we must do it within the Dockerfile
RUN mkdir -p /app/temp

EXPOSE 5000
CMD ["python", "server.py"]
#CMD flask --app server run --host=0.0.0.0