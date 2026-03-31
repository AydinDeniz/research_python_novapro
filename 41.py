from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import os
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Generate a small preview
        preview_filename = f"preview_{filename}"
        preview_filepath = os.path.join(app.config['UPLOAD_FOLDER'], preview_filename)
        with Image.open(filepath) as img:
            img.thumbnail((100, 100))
            img.save(preview_filepath)
        
        return render_template('preview.html', filename=preview_filename)
    return "File type not allowed", 400

@app.route('/preview/<filename>')
def preview_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(filepath):
        return "File not found", 404
    return send_file(filepath, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)