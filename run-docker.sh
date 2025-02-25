if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <media_file> <output_file>"
    exit 1
fi

MEDIA_FILE=$(readlink -f "$1")
OUTPUT_FILE=$(readlink -f "$2")

docker run --rm -v "$(dirname "$MEDIA_FILE"):/input" -v "$(dirname "$OUTPUT_FILE"):/output" \
       -w /input jambur-speech-filter --media_file "/input/$(basename "$MEDIA_FILE")" \
       --output_file "/output/$(basename "$OUTPUT_FILE")"