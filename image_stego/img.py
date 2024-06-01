from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import filedialog
import heapq
from collections import defaultdict
import os

import termcolor
from termcolor import colored
from pyfiglet import figlet_format

class HuffmanNode:
    def _init_(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def _lt_(self, other):
        return self.freq < other.freq

class ImageSteg:
    def _init_(self):
        pass

    # Methods for Huffman Coding
    def build_huffman_tree(self, text):
        frequency = defaultdict(int)
        for char in text:
            frequency[char] += 1

        priority_queue = [HuffmanNode(char, freq) for char, freq in frequency.items()]
        heapq.heapify(priority_queue)

        while len(priority_queue) > 1:
            left = heapq.heappop(priority_queue)
            right = heapq.heappop(priority_queue)
            merged = HuffmanNode(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            heapq.heappush(priority_queue, merged)

        return priority_queue[0]

    def build_huffman_codes(self, root, prefix="", codes=None):
        if codes is None:
            codes = {}
        if root is not None:
            if root.char is not None:
                codes[root.char] = prefix
            self.build_huffman_codes(root.left, prefix + "0", codes)
            self.build_huffman_codes(root.right, prefix + "1", codes)
        return codes

    def huffman_compress(self, text):
        root = self.build_huffman_tree(text)
        codes = self.build_huffman_codes(root)
        encoded_text = "".join(codes[char] for char in text)
        return encoded_text, codes

    def huffman_decompress(self, text, codes):
        decoded_text = ""
        current_code = ""
        for bit in text:
            current_code += bit
            for char, code in codes.items():
                if code == current_code:
                    decoded_text += char
                    current_code = ""
                    break
        return decoded_text

    # Method for Run-Length Encoding
    def rle_compress(self, text):
        encoded_text = ""
        count = 1
        for i in range(1, len(text)):
            if text[i] == text[i - 1]:
                count += 1
            else:
                encoded_text += str(count) + text[i - 1]
                count = 1
        encoded_text += str(count) + text[-1]
        return encoded_text

    def rle_decompress(self, text):
        decoded_text = ""
        i = 0
        while i < len(text):
            count = int(text[i])
            char = text[i + 1]
            decoded_text += char * count
            i += 2
        return decoded_text

    def __fillMSB(self, inp):
        '''
        0b01100 -> [0,0,0,0,1,1,0,0]
        '''
        inp = inp.split("b")[-1]
        inp = '0'*(7-len(inp))+inp
        return [int(x) for x in inp]

    def __decrypt_pixels(self, pixels):
        '''
        Given list of 7 pixel values -> Determine 0/1 -> Join 7 0/1s to form binary -> integer -> character
        '''
        pixels = [str(x%2) for x in pixels]
        bin_repr = "".join(pixels)
        return chr(int(bin_repr,2))

    def encrypt_text_in_image(self, image_path, msg, password, target_path=""):
        '''
        Read image -> Flatten -> encrypt images using LSB -> reshape and repack -> return image
        '''
        img = np.array(Image.open(image_path))
        imgArr = img.flatten()
        
        # Concatenate the message and password with a unique separator
        secret_message = f"{msg}<-SEP->{password}<-END->"
        msgArr = [self.__fillMSB(bin(ord(ch))) for ch in secret_message]
        
        idx = 0
        for char in msgArr:
            for bit in char:
                if bit == 1:
                    if imgArr[idx] == 0:
                        imgArr[idx] = 1
                    else:
                        imgArr[idx] = imgArr[idx] if imgArr[idx] % 2 == 1 else imgArr[idx] - 1
                else: 
                    if imgArr[idx] == 255:
                        imgArr[idx] = 254
                    else:
                        imgArr[idx] = imgArr[idx] if imgArr[idx] % 2 == 0 else imgArr[idx] + 1   
                idx += 1
            
        filename = os.path.basename(image_path)
        savePath = os.path.join(target_path, filename.split(".")[0] + "_embedded.png")

        resImg = Image.fromarray(np.reshape(imgArr, img.shape))
        resImg.save(savePath)
        return savePath

    def decrypt_text_in_image(self, image_path, password):
        '''
        Read image -> Extract Text -> Return
        '''
        img = np.array(Image.open(image_path))
        imgArr = np.array(img).flatten()
        
        decrypted_message = ""
        password_matched = False
        
        for i in range(7, len(imgArr), 7):
            decrypted_char = self.__decrypt_pixels(imgArr[i-7:i])
            decrypted_message += decrypted_char
            
            if decrypted_message.endswith("<-END->"):
                # Split the message and password using the separator
                parts = decrypted_message.split("<-SEP->")
                extracted_password = parts[-1].split("<-END->")[0]
                extracted_message = "<-SEP->".join(parts[:-1])
                
                if extracted_password.strip() == password.strip():
                    password_matched = True
                    return extracted_message
                else:
                    return "Invalid password"

        return "Invalid password"


def get_user_choice():
    while True:
        try:
            choice = int(input("Enter your choice: "))
            return choice
        except ValueError:
            print("Invalid input. Please enter a valid choice.")

def get_user_input(prompt):
    while True:
        user_input = input(prompt)
        return user_input

def encode_message():
    img = ImageSteg()
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Ask user to select an image file
    print("\tSelect the file")
    # Hide the window
    root.attributes('-alpha', 0.0)
    # Always have it on top
    root.attributes('-topmost', True)
    image_path = filedialog.askopenfilename(title="Select an image to hide the message")

    if image_path:
        msg = get_user_input("Enter the message to hide in the image: ")
        password = get_user_input("Enter the password to encrypt the message: ")
        output_folder = filedialog.askdirectory(title="Select a folder to save the stego image")
        if output_folder:
            img.encrypt_text_in_image(image_path, msg, password, output_folder)
        print("\n\tEncoding underway ! Please wait ... \n\n")
        print("Message hidden in the image.")
        print("Stego image saved at:", output_folder)


def decode_message():
    img = ImageSteg()
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Ask user to select an image file
    print("\tSelect the file")
    # Hide the window
    root.attributes('-alpha', 0.0)
    # Always have it on top
    root.attributes('-topmost', True)
    image_path = filedialog.askopenfilename(title="Select an image to decode the message")

    if image_path:
        password = get_user_input("Enter the password to decrypt the message: ")
        decoded_msg = img.decrypt_text_in_image(image_path, password)
        print("\n\tDecoded message:", decoded_msg)


def main():
    print(colored(figlet_format("InvisoCloak"), color='red'))
    while True:
        print("\nSELECT THE IMAGE STEGANOGRAPHY OPERATION\n")
        print("1. Encode message into an image")
        print("2. Decode message from an image")
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