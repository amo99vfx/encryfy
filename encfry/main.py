import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# ==============================
# KEY GENERATION
# ==============================

def derive_key(password, salt):
    """Convert password into a secure 256-bit AES key."""

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000
    )

    return kdf.derive(password.encode("utf-8"))


# ==============================
# ENCRYPT IMAGE
# ==============================

def encrypt_image(input_file, output_file, password):

    with open(input_file, "rb") as file:
        image_data = file.read()

    # Generate random salt
    salt = os.urandom(16)

    # Generate random nonce
    nonce = os.urandom(12)

    # Generate encryption key
    key = derive_key(password, salt)

    # AES-256-GCM encryption
    aes = AESGCM(key)

    encrypted_data = aes.encrypt(
        nonce,
        image_data,
        None
    )

    # Save salt + nonce + encrypted data
    with open(output_file, "wb") as file:
        file.write(salt)
        file.write(nonce)
        file.write(encrypted_data)


# ==============================
# DECRYPT IMAGE
# ==============================

def decrypt_image(input_file, output_file, password):

    with open(input_file, "rb") as file:
        encrypted_data = file.read()

    # Extract salt
    salt = encrypted_data[:16]

    # Extract nonce
    nonce = encrypted_data[16:28]

    # Extract encrypted image
    ciphertext = encrypted_data[28:]

    # Generate same key
    key = derive_key(password, salt)

    # AES-256-GCM decryption
    aes = AESGCM(key)

    decrypted_data = aes.decrypt(
        nonce,
        ciphertext,
        None
    )

    # Save recovered image
    with open(output_file, "wb") as file:
        file.write(decrypted_data)


# ==============================
# ENCRYPT BUTTON
# ==============================

def encrypt_button():

    input_file = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[
            ("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp"),
            ("All Files", "*.*")
        ]
    )

    if not input_file:
        return

    password = simpledialog.askstring(
        "Encryption Password",
        "Enter password:",
        show="*"
    )

    if not password:
        return

    output_file = filedialog.asksaveasfilename(
        title="Save Encrypted File",
        defaultextension=".enc",
        filetypes=[
            ("Encrypted File", "*.enc")
        ]
    )

    if not output_file:
        return

    try:

        encrypt_image(
            input_file,
            output_file,
            password
        )

        messagebox.showinfo(
            "Success",
            "Image encrypted successfully!\n\n"
            f"Saved as:\n{output_file}"
        )

    except Exception as error:

        messagebox.showerror(
            "Encryption Error",
            str(error)
        )


# ==============================
# DECRYPT BUTTON
# ==============================

def decrypt_button():

    input_file = filedialog.askopenfilename(
        title="Select Encrypted File",
        filetypes=[
            ("Encrypted Files", "*.enc"),
            ("All Files", "*.*")
        ]
    )

    if not input_file:
        return

    password = simpledialog.askstring(
        "Decryption Password",
        "Enter password:",
        show="*"
    )

    if not password:
        return

    output_file = filedialog.asksaveasfilename(
        title="Save Decrypted Image",
        defaultextension=".png",
        filetypes=[
            ("PNG Image", "*.png"),
            ("JPEG Image", "*.jpg"),
            ("All Files", "*.*")
        ]
    )

    if not output_file:
        return

    try:

        decrypt_image(
            input_file,
            output_file,
            password
        )

        messagebox.showinfo(
            "Success",
            "Image decrypted successfully!\n\n"
            f"Saved as:\n{output_file}"
        )

    except Exception:

        messagebox.showerror(
            "Decryption Failed",
            "Incorrect password or invalid encrypted file."
        )


# ==============================
# GUI
# ==============================

root = tk.Tk()

root.title("Image Encryption & Decryption")
root.geometry("500x350")
root.resizable(False, False)


# Title

title = tk.Label(
    root,
    text="🔐 Image Encryption & Decryption",
    font=("Arial", 20, "bold")
)

title.pack(pady=35)


# Description

description = tk.Label(
    root,
    text="Secure your images using AES-256-GCM",
    font=("Arial", 11)
)

description.pack(pady=5)


# Encrypt button

encrypt_btn = tk.Button(
    root,
    text="🔒 Encrypt Image",
    command=encrypt_button,
    width=25,
    height=2,
    font=("Arial", 12)
)

encrypt_btn.pack(pady=20)


# Decrypt button

decrypt_btn = tk.Button(
    root,
    text="🔓 Decrypt Image",
    command=decrypt_button,
    width=25,
    height=2,
    font=("Arial", 12)
)

decrypt_btn.pack(pady=5)


# Footer

footer = tk.Label(
    root,
    text="AES-256-GCM  •  PBKDF2  •  SHA-256",
    font=("Arial", 9)
)

footer.pack(side="bottom", pady=20)


# Start application

root.mainloop()