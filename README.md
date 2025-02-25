# Jambur-Speech-Filter
A Python project which filters certain words and phrases from audio/video

This project utilizes a local build of [FFmpeg](https://ffmpeg.org) as a dependency. The local FFmpeg will be automatically configured for use if no existing FFmpeg installation is found in your system's PATH.

# Setup
To setup this project, we begin by ensuring Python is installed: [Python Download](https://www.python.org/downloads/). It's recommended to create a virtual environment before installing the requirements to prevent conflicts with your existing python setup. You can then install the necessary packages by running the following command in the project root directory: `pip install -r ./requirements.txt`.

# Tutorial
This is a tutorial showing how to run this project once setup.

note: The command's shown should be run in the root directory of this project.

To filter phrases out of the desired audio / video file we can run this command `python run.py --media_file test.mp4 --output_file test_modified.mp4 --audio_bitrate 192k` which can work on both audio and video files but both the media_file and output_file both need to be the same format (e.x. audio in = audio out, video in = video out).

# Updating Filter List
> **WARNING**: The current filter list includes exposed words or phrases that might be considered offensive, given its customizable nature. These words are not intended to offend; their presence is solely for the purpose of filtering such language.
```
+-- filters
    +-- filtered_phrases.txt
```
If you want to update the filter list you can open `./filters/filtered_phrases.txt` and add a new line for each new phrase you want filtered out.

Note: Currently a limitation of the project is that only individual words can be filtered and not multi word phrases which is planned to be implemented in the future.