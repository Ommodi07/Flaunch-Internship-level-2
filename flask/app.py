from flask import Flask, request, render_template, redirect
import keras_ocr
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize the Keras OCR pipeline
pipeline = keras_ocr.pipeline.Pipeline()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        text = extract_text(filepath)
        return render_template('result.html', text=text)

def extract_text(image_path):
    # Open image using PIL
    image = keras_ocr.tools.read(image_path)
    
    # Perform OCR using Keras OCR pipeline
    prediction_groups = pipeline.recognize([image])

    # Extract the text from the OCR predictions
    text = ' '.join([text for _, text in prediction_groups[0]])

    return text

if __name__ == '__main__':
    app.run(debug=True)
