from flask import Flask, request, send_file, send_from_directory
import os
import zipfile
import pyzstd
from io import BytesIO

app = Flask(__name__)

# Compression function
def mahoa(file_data, ZSTD_DICT):
    compressed_magic_number = b"\x22\x4a\x67\x00"
    if compressed_magic_number not in file_data:
        try:
            compressed_data = bytearray(pyzstd.compress(file_data, 17, pyzstd.ZstdDict(ZSTD_DICT, True)))
            compressed_data[0:0] = len(file_data).to_bytes(4, byteorder="little", signed=False)
            compressed_data[0:0] = b"\x22\x4a\x00\xef"
            return compressed_data, None
        except Exception as e:
            return file_data, None
    return file_data, None

def giai(file_data, ZSTD_DICT):
    magic_number = b"\x28\xb5\x2f\xfd"
    if magic_number in file_data:
        file_data = file_data[file_data.find(magic_number):]
        try:
            decompressed_data = pyzstd.decompress(file_data, pyzstd.ZstdDict(ZSTD_DICT, True))
            return decompressed_data, None
        except Exception as e:
            return file_data, None
    return file_data, None

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part in the request", 400

    action = request.form.get('action')
    ZSTD_DICT = open('DICT', 'rb').read()
    files = request.files.getlist('file')

    # Check for missing action
    if not action:
        return "Missing action (compress/decompress)", 400

    print(f"Action: {action}")
    print(f"Files received: {len(files)}")

    # Create a zip archive in memory
    zip_buffer = BytesIO()

    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_archive:
            for file in files:
                filename = file.filename
                file_data = file.read()

                print(f"Processing file: {filename}")

                if action == 'compress':
                    # Compress each file
                    compressed_data, error = mahoa(file_data, ZSTD_DICT)
                    if error:
                        return error, 400
                    # Add compressed data to the ZIP file with the original filename
                    zip_archive.writestr(filename, compressed_data)  # No .zst extension
                    print(f"Compressed data added for: {filename}")

                elif action == 'decompress':
                    # Decompress each file
                    decompressed_data, error = giai(file_data, ZSTD_DICT)
                    if error:
                        return error, 400
                    # Add decompressed data to the ZIP file with the original filename
                    zip_archive.writestr(filename, decompressed_data)  # Restore original filename
                    print(f"Decompressed data added for: {filename}")

                else:
                    return "Invalid action", 400

    except Exception as e:
        print(f"Error: {e}")
        return f"An error occurred: {e}", 500

    zip_buffer.seek(0)

    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='output.zip')

if __name__ == '__main__':
    app.run(debug=True)
