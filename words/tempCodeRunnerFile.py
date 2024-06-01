from flask import Flask, render_template, request
import binascii
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2

app = Flask(__name__)

def generate_private_key(password):
    salt = b"this is a salt"
    kdf = PBKDF2(password, salt, 64, 1000)
    key = kdf[:32]
    return key

def encrypt_message(password, message):
    key = generate_private_key(password)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    encrypted_bytes = iv + cipher.encrypt(message.encode('utf-8'))
    encrypted_hex = binascii.hexlify(encrypted_bytes).decode('utf-8')
    return encrypted_hex

def decrypt_message(password, encrypted_hex):
    try:
        encrypted_bytes = binascii.unhexlify(encrypted_hex.encode('utf-8'))
        iv = encrypted_bytes[:AES.block_size]
        cipher = AES.new(generate_private_key(password), AES.MODE_CFB, iv)
        decrypted_bytes = cipher.decrypt(encrypted_bytes[AES.block_size:])
        decrypted_message = decrypted_bytes.decode('utf-8')
        return decrypted_message
    except (ValueError, KeyError):
        return "Decryption failed. Invalid stego text or password."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/embed', methods=['POST'])
def embed():
    secret_message = request.form['secret_message']
    password = request.form['password']
    if not secret_message or not password:
        return "Please provide both a secret message and a password."
    stego_text = encrypt_message(password, secret_message)
    return render_template('result.html', stego_text=stego_text)

@app.route('/reveal', methods=['POST'])
def reveal():
    stego_text = request.form['stego_text']
    password = request.form['password']
    if not stego_text or not password:
        return "Please provide both stego text and a password."
    secret_message = decrypt_message(password, stego_text)
    return render_template('result.html', secret_message=secret_message)

if __name__ == "__main__":
    app.run(debug=True)
