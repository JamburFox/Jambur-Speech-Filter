@echo off
SET IMAGE_NAME=jambur-speech-filter

docker images %IMAGE_NAME% --format "{{.Repository}}" | findstr /i %IMAGE_NAME% >nul
IF ERRORLEVEL 1 (
    echo Image %IMAGE_NAME% not found. Please build it first.
    exit /b
) ELSE (
    docker run -p 5000:5000 --gpus all %IMAGE_NAME%
    timeout /t 3 /nobreak >nul
    start http://localhost:5000
)