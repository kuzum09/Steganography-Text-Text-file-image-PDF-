from flask import Flask, render_template, request, redirect, url_for
import os
from TextStegano import txt_encode, txt_decode

app = Flask(__name__)

# Define the routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode_text', methods=['GET', 'POST'])
def encode_text():
    if request.method == 'POST':
        # Get form data
        cover_file = request.files['cover_file']
        text_message = request.form['text_message']
        password = request.form['password']
        
        # Define the output folder
        output_folder = 'uploads/encoded'
        
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Save the uploaded file to a temporary location
        temp_cover_file = os.path.join(output_folder, cover_file.filename)
        cover_file.save(temp_cover_file)
        
        # Encode text into file and save
        stego_text_file = txt_encode(text_message, password, temp_cover_file, output_folder)
        
        # Remove the temporary file
        os.remove(temp_cover_file)

        return render_template('encode_result.html', stego_text_file=stego_text_file)
    return render_template('encode.html')

@app.route('/decode_text', methods=['GET', 'POST'])
def decode_text():
    if request.method == 'POST':
        # Get form data
        stego_text_file = request.files['stego_text_file']
        password = request.form['password']  # Retrieve the password from the form
        
        # Define the output folder
        output_folder = 'uploads/decoded'
        
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Save the uploaded file to a temporary location
        temp_stego_file = os.path.join(output_folder, stego_text_file.filename)
        stego_text_file.save(temp_stego_file)
        
        # Decode text from file, passing the password
        decoded_message = txt_decode(temp_stego_file, password)
        
        # Remove the temporary file
        os.remove(temp_stego_file)

        return render_template('decode_result.html', decoded_message=decoded_message)
    return render_template('decode.html')

if __name__ == "__main__":
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.run(debug=True)
