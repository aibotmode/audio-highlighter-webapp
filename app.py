from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Home route redirects to upload form
@app.route('/')
def index():
    return redirect(url_for('upload_file'))

# Upload form and file processing
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if 'file' is in request
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        # Check if file is selected
        if file.filename == '':
            return "No selected file", 400
        # If file is valid, save and confirm
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            return f"File uploaded successfully: {file.filename}"
    # Render the upload form if GET request
    return render_template('upload.html')

# Run app locally (this line won't affect Render)
if __name__ == '__main__':
    app.run(debug=True)
