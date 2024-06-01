from flask import Flask, render_template, request
import os
from pdf import embed_message_into_pdf,decode_message_from_pdf

app = Flask(__name__)

# Define the routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        # Get form data
        cover_pdf_file = request.files['cover_pdf']
        message = request.form['message']
        password = request.form['password']
        
        # Define the output folder
        output_folder = 'uploads/encoded'
        
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Save the uploaded file to a temporary location
        temp_cover_pdf_file = os.path.join(output_folder, cover_pdf_file.filename)
        cover_pdf_file.save(temp_cover_pdf_file)
        
        # Embed message into PDF and save
        stego_pdf_file = embed_message_into_pdf(temp_cover_pdf_file, message, password, output_folder)
        
        # Remove the temporary file
        os.remove(temp_cover_pdf_file)

        return render_template('encode_result.html', stego_pdf_file=stego_pdf_file)
    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        # Handle form submission
        stego_pdf_file = request.files['stego_pdf']
        password = request.form['password']
        decoded_message = decode_message_from_pdf(stego_pdf_file, password)
        return render_template('decode_result.html', decoded_message=decoded_message)
    return render_template('decode.html')

if __name__ == "__main__":
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.run(debug=True,port=8000)