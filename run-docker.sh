if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <media_file> <output_file> <audio_bitrate>"
    exit 1
fi
MEDIA_FILE=$(readlink -f "$1")
OUTPUT_FILE=$(readlink -f "$2")
AUDIO_BITRATE="$3"
docker run --gpus all --rm -v "$(dirname "$MEDIA_FILE"):/input" -v "$(dirname "$OUTPUT_FILE"):/output" \
       -w /input jambur-speech-filter --media_file "/input/$(basename "$MEDIA_FILE")" \
       --output_file "/output/$(basename "$OUTPUT_FILE")" --audio_bitrate "$AUDIO_BITRATE"