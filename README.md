# Jambur-Speech-Filter
A Python project which filters certain words and phrases from audio/video

This project utilizes a local build of [FFmpeg](https://ffmpeg.org) as a dependency. The local FFmpeg will be automatically configured for use if no existing FFmpeg installation is found in your system's PATH.

# Setup (Docker)
To setup this project, we begin by ensuring Docker is installed: [Docker Download](https://www.docker.com/). After Docker is downloaded and installed you can then run `build-docker.bat` on windows or `build-docker.sh` on linux / mac to build the docker Image.

If preferred you can execute the following command while in the project root directory: `docker build -t jambur-speech-filter .`.

# Tutorial (Docker)
After the docker image is built using the above setup steps we can then run this project by running `run-docker.bat` for windows or `run-docker.sh` for linux / mac which will start the server. This should also automatically launch a new browser tab after 3 seconds but you can open `http://localhost:5000` in your browser any time to access the server.

If preferred you can execute the following command while in the project root directory: `docker run -p 5000:5000 --gpus all jambur-speech-filter`and open `http://localhost:5000` in your browser.

# Setup (Python)
To setup this project, we begin by ensuring Python is installed: [Python Download](https://www.python.org/downloads/). It's recommended to create a virtual environment before installing the requirements to prevent conflicts with your existing python setup. You can then install the necessary packages by running the following command in the project root directory: `pip install -r ./requirements.txt`.

# Tutorial (Python)
After the python setup is down we can run this project by running `run-python.bat` for windows or `run-python.sh` for linux / mac which will start the server. This should also automatically launch a new browser tab after 3 seconds but you can open `http://localhost:5000` in your browser any time to access the server.

If preferred you can execute the following command while in the project root directory: `flask --app server run --host=0.0.0.0`and open `http://localhost:5000` in your browser.

# Tutorial (Python Commandline)
To filter phrases out of the desired audio / video file we can run this command in the project root directory `python run.py --media_file test.mp4 --output_file test_modified.mp4 --audio_bitrate 192k` which can work on both audio and video files but both the media_file and output_file both need to be the same format (e.x. audio in = audio out, video in = video out).

test.mp4 can be replaced with the location of any audio or video file you want to filter and test_modified.mp4 can be replaced with the name of the audio or video output save location. --audio_bitrate (by default 192k) can also be set to customize the audio bitrate of the modified file.

You can also add the argument `--filter_file xyz.wav` to play audio over the muted segments.

# Updating Filter List
> **WARNING**: The current filter list includes exposed words or phrases that might be considered offensive, given its customizable nature. These words are not intended to offend; their presence is solely for the purpose of filtering such language.
```
+-- filters
    +-- filtered_phrases.txt
```
If you want to update the filter list you can open `./filters/filtered_phrases.txt` and add a new line for each new phrase you want filtered out.

Note: Currently a limitation of the project is that only individual words can be filtered and not multi word phrases which is planned to be implemented in the future.