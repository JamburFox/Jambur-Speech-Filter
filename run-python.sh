#!/bin/bash
flask --app server run --host=0.0.0.0 &

sleep 3

if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:5000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:5000
else
    echo "Unsupported OS"
fi