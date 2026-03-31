from flask import Flask, request, send_file, abort, jsonify
import os
import uuid
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Dictionary to store file metadata
file_metadata = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file"), 400
    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Generate a temporary URL
        file_id = str(uuid.uuid4())
        file_metadata[file_id] = {
            'filepath': filepath,
            'uploaded_at': time.time(),
            'downloaded': False
        }
        
        return jsonify(file_id=file_id), 201
    return jsonify(error="File type not allowed"), 400

@app.route('/download/<file_id>')
def download_file(file_id):
    if file_id not in file_metadata:
        abort(404)
    
    metadata = file_metadata[file_id]
    current_time = time.time()
    
    # Check if the file has expired or been downloaded
    if metadata['downloaded'] or (current_time - metadata['uploaded_at']) > 600:
        abort(404)
    
    # Mark the file as downloaded
    metadata['downloaded'] = True
    
    return send_file(metadata['filepath'], as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)