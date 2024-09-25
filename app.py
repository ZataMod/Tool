from flask import Flask, render_template, request
import os
import pyzstd

app = Flask(__name__)

def giai(file_path,ZSTD_DICT):
	dl=open(file_path,'rb').read()
	if dl.find(b"\x28\xb5\x2f\xfd")!=-1:
		dl = dl[dl.find(b"\x28\xb5\x2f\xfd"):]
		try:
			dl = pyzstd.decompress(dl, pyzstd.ZstdDict(ZSTD_DICT, True))
		except:
				return 0
		with open(file_path, "wb") as output_file_path:
				output_file_path.write(dl)
				return 1
	return f"{file_path} đã được giải nén."
def mahoa(file_path,ZSTD_DICT):
	dl=open(file_path,'rb').read()
	dlg=dl
	if dl.find(b"\x22\x4a\x67\x00")==-1:
		try:
			dl = bytearray(pyzstd.compress(dl,17,pyzstd.ZstdDict(ZSTD_DICT, True)))                
			dl[0:0] = len(dlg).to_bytes(4, byteorder="little", signed=False)
			dl[0:0] = b"\x22\x4a\x00\xef"
		except:
			return 0
		with open(file_path, "wb") as output_file_path:
				    output_file_path.write(dl)
				    return 1
	return f"{file_path} đã được nén."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    ZSTD_DICT=open('DICT','rb').read()
    files = request.files.getlist('file')
    action = request.form['action']
    messages = []

    uploads_dir = 'uploads/OUP'
    os.makedirs(uploads_dir, exist_ok=True)

    for file in files:
        if file:
            file_path = os.path.join(uploads_dir, file.filename)
            file.save(file_path)

            if action == 'compress':
                messages.append(mahoa(file_path,ZSTD_DICT))
            elif action == 'decompress':
                messages.append(giai(file_path,ZSTD_DICT))
    if action == 'compress':return 'Đã Mã Hoá'
    elif action == 'decompress':return 'Đã  Giải'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)