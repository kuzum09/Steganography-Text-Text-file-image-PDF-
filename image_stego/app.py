from flask import Flask, render_template, request, redirect, url_for
from img import ImageSteg
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        msg = request.form['message']
        password = request.form['password']
        img = ImageSteg()
        output_folder = 'uploads/encoded'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        image_file = request.files['image']
        image_path = os.path.join(output_folder, image_file.filename)
        image_file.save(image_path)
        stego_image = img.encrypt_text_in_image(image_path, msg, password, output_folder)
        os.remove(image_path)  # Remove the original image after encoding
        return render_template('encode_result.html', stego_image=stego_image)
    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        password = request.form['password']
        img = ImageSteg()
        output_folder = 'uploads/decoded'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        stego_image_file = request.files['stego_image']
        stego_image_path = os.path.join(output_folder, stego_image_file.filename)
        stego_image_file.save(stego_image_path)
        decoded_message = img.decrypt_text_in_image(stego_image_path, password)
        os.remove(stego_image_path)  # Remove the stego image after decoding
        return render_template('decode_result.html', decoded_message=decoded_message)
    return render_template('decode.html')

if __name__ == "__main__":
    app.run(debug=True, port=8090)
