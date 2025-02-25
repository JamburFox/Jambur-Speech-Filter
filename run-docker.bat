@echo off
if "%~3"=="" (
    echo Usage: %0 media_file output_file audio_bitrate
    exit /b 1
)
set MEDIA_FILE=%~dp1%~nx1
set OUTPUT_FILE=%~dp2%~nx2
set AUDIO_BITRATE=%3
docker run --gpus all --rm -v "%~dp1:/input" -v "%~dp2:/output" ^
       -w /input jambur-speech-filter --media_file "/input/%~nx1" ^
       --output_file "/output/%~nx2" --audio_bitrate "%AUDIO_BITRATE%"