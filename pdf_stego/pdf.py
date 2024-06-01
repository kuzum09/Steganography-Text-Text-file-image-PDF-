import tkinter as tk
from tkinter import filedialog
import os
from PyPDF2 import PdfReader, PdfWriter
from pyfiglet import figlet_format
from termcolor import colored

def select_cover_pdf():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    print("\tSelect the cover PDF file")
    # Hide the window
    root.attributes('-alpha', 0.0)
    # Always have it on top
    root.attributes('-topmost', True)
    cover_file = filedialog.askopenfilename(title="Select Cover PDF File")
    return cover_file

def select_output_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    print("\tSelect the output folder")
    # Hide the window
    root.attributes('-alpha', 0.0)
    # Always have it on top
    root.attributes('-topmost', True)
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    return output_folder

def embed_message_into_pdf(cover_pdf_file, message, password, output_folder):
    # Open the cover PDF file
    reader = PdfReader(cover_pdf_file)
    writer = PdfWriter()

    # Clone the document from the reader
    writer.append_pages_from_reader(reader)

    # Embed the message and password in the PDF metadata
    writer.add_metadata({
        '/Message': message,
        '/Password': password
    })

    # Save the modified PDF file
    stego_pdf_file = os.path.join(output_folder, 'stego_' + os.path.basename(cover_pdf_file))
    writer.write(stego_pdf_file)

    return stego_pdf_file

def decode_message_from_pdf(stego_pdf_file, entered_password):
    # Open the stego PDF file
    reader = PdfReader(stego_pdf_file)

    # Extract the embedded message and password from the PDF metadata
    embedded_message = reader.metadata.get('/Message')
    embedded_password = reader.metadata.get('/Password')

    # Verify the password
    if embedded_password == entered_password:
        return embedded_message
    else:
        return "Incorrect password. Access denied."

def get_user_choice():
    try:
        choice = int(input("Enter your choice: "))
        return choice
    except ValueError:
        return None

def encode_message():
    cover_pdf_file = select_cover_pdf()

    message = input("Enter the secret message: ")
    password = input("Enter the password to encrypt the message: ")

    
    output_folder = select_output_folder()

    stego_pdf_file = embed_message_into_pdf(cover_pdf_file, message, password, output_folder)
    print("Stego file saved at:", stego_pdf_file)

def decode_message():
    stego_pdf_file = select_cover_pdf()
    entered_password = input("Enter the password to decode the message: ")
    decoded_message = decode_message_from_pdf(stego_pdf_file, entered_password)
    print("Decoded Message:", decoded_message)

def main():
    print(colored(figlet_format("InvisoCloak"), color='red'))
    while True:
        print("\nSELECT THE STEGANOGRAPHY OPERATION\n")
        print("1. Encode message into a PDF")
        print("2. Decode message from a PDF")
        print("3. Exit")

        choice = get_user_choice()

        if choice == 1:
            encode_message()

        elif choice == 2:
            decode_message()
        elif choice == 3:
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()
