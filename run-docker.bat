@echo off
if "%~2"=="" (
    echo Usage: %0 media_file output_file
    exit /b 1
)

set MEDIA_FILE=%~dp1%~nx1
set OUTPUT_FILE=%~dp2%~nx2

docker run --rm -v "%~dp1:/input" -v "%~dp2:/output" ^
       -w /input jambur-speech-filter --media_file "/input/%~nx1" ^
       --output_file "/output/%~nx2"