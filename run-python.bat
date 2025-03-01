@echo off
start cmd /k flask --app server run --host=0.0.0.0

timeout /t 3 /nobreak >nul

start http://localhost:5000