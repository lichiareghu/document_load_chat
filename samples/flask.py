from flask import Flask, request, jsonify, send_from_directory
import os
import time
import threading

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DOCS_FOLDER = 'docs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOCS_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        return jsonify({"status": "success", "filename": file.filename})
    return jsonify({"status": "error", "message": "No file uploaded"})

@app.route('/process', methods=['POST'])
def process_file():
    def long_task():
        time.sleep(5)  # Simulate a long-running task

    thread = threading.Thread(target=long_task)
    thread.start()
    return jsonify({"status": "processing", "message": "File processing started."})

@app.route('/list-docs', methods=['GET'])
def list_docs():
    files = os.listdir(DOCS_FOLDER)
    return jsonify({"files": files})

@app.route('/load-chat/<filename>', methods=['GET'])
def load_chat(filename):
    file_path = os.path.join(DOCS_FOLDER, filename)
    if os.path.exists(file_path):
        return jsonify({"status": "success", "message": f"Chat loaded for {filename}"})
    return jsonify({"status": "error", "message": "File not found"})

if __name__ == '__main__':
    app.run(debug=True)
