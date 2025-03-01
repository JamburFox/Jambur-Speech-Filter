console.log("hello world")

async function submitForm() {
    try {
        const formData = new FormData(document.getElementById('fileForm'));

        document.getElementById('result').textContent = "Processing...";

        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        })
        const contentType = response.headers.get('content-type');
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const mediaContainer = document.getElementById('media-container');
        let mediaElement;

        if (contentType.startsWith("video/")) {
            mediaElement = document.createElement('video');
            mediaElement.controls = true;
            mediaElement.src = url;
            mediaElement.width = 640;
        } else if (contentType.startsWith('audio/')) {
            mediaElement = document.createElement('audio');
            mediaElement.controls = true;
            mediaElement.src = url;
        }

        if (mediaElement) {
            mediaContainer.appendChild(mediaElement);
        }

        document.getElementById('result').textContent = "Done!";

        const downloadButton = document.getElementById('download-button');
        downloadButton.addEventListener('click', () => {
            const a = document.createElement('a');
            a.href = url;
            a.download = "file";
            a.click();
        });
    } catch (error) {
        document.getElementById('result').textContent = "Error!";
        console.error('Error fetching media:', error);
    }
}