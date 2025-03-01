from flask import Flask, render_template, request, send_file, jsonify
import io
import os
from run import process_file, get_temp_path, create_temp_folder
from jambur_speech_filter.utils import delete_file 

app = Flask(__name__,
            static_folder='webapp/static',
            template_folder='webapp')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return "No file uploaded", 400
     
    file = request.files['file']
    filename = file.filename
    file_extension = os.path.splitext(filename)[1]
    save_path = get_temp_path(f"temp_download{file_extension}")
    out_path = get_temp_path(f"temp_processed{file_extension}")

    with io.BytesIO(file.read()) as buffer:
        with open(get_temp_path(save_path), 'wb') as out_file:
            out_file.write(buffer.getbuffer())

    file_location = process_file(save_path, out_path)
    if not file_location:
        return "Error processing Media", 500

    with open(file_location, 'rb') as file:
        file_data = file.read()
    upload_buffer = io.BytesIO(file_data)

    #cleanup temp folder
    delete_file(save_path)
    delete_file(out_path)

    return send_file(
        upload_buffer,
        as_attachment=True,
        download_name=f'processed_output{file_extension}'
    )

if __name__ == "__main__":
    create_temp_folder()
    app.run(host='0.0.0.0', debug=True)