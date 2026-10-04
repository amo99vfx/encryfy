import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from animal_images import create_animal_image

# LSB
from image_codec import (
    hide_data as lsb_hide_data,
    get_capacity_bytes as lsb_capacity
)

# DCT
from dct_codec import (
    hide_data as dct_hide_data,
    get_capacity_bytes as dct_capacity
)


# ============================================================
# ENCRYPTION SETTINGS
# ============================================================

PBKDF2_ITERATIONS = 600_000
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32


# ============================================================
# KEY DERIVATION
# ============================================================

def derive_key(password, salt):

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS
    )

    return kdf.derive(
        password.encode("utf-8")
    )


# ============================================================
# ENCRYPT MESSAGE
# ============================================================

def encrypt_message(message, password):

    salt = os.urandom(
        SALT_SIZE
    )

    key = derive_key(
        password,
        salt
    )

    nonce = os.urandom(
        NONCE_SIZE
    )

    aes = AESGCM(key)

    ciphertext = aes.encrypt(
        nonce,
        message.encode("utf-8"),
        None
    )

    return salt + nonce + ciphertext


# ============================================================
# PASSWORD SHOW / HIDE
# ============================================================

def toggle_password():

    if password_entry.cget("show") == "":

        password_entry.config(
            show="•"
        )

        show_password_button.config(
            text="👁"
        )

    else:

        password_entry.config(
            show=""
        )

        show_password_button.config(
            text="🙈"
        )


# ============================================================
# METHOD CHANGE
# ============================================================

def method_changed(event=None):

    method = method_var.get()

    if method == "LSB Substitution":

        method_info.config(
            text=(
                "Fast • High capacity • "
                "Pixel-domain steganography"
            )
        )

    elif method == "DCT Transform Domain":

        method_info.config(
            text=(
                "Frequency-domain • "
                "More resistant to compression"
            )
        )


# ============================================================
# ENCRYPT + CREATE IMAGE
# ============================================================

def encrypt_and_create():

    message = message_box.get(
        "1.0",
        tk.END
    ).strip()

    password = password_entry.get()

    method = method_var.get()

    if not message:

        messagebox.showwarning(
            "Missing Message",
            "Please enter a secret message."
        )

        return

    if not password:

        messagebox.showwarning(
            "Missing Password",
            "Please enter a password."
        )

        return

    try:

        encrypt_button.config(
            state="disabled"
        )

        # ----------------------------------------------------
        # Encrypt
        # ----------------------------------------------------

        status_label.config(
            text="🔐 Encrypting..."
        )

        root.update()

        encrypted_data = encrypt_message(
            message,
            password
        )

        # ----------------------------------------------------
        # Generate animal
        # ----------------------------------------------------

        status_label.config(
            text="🎨 Creating a unique animal..."
        )

        root.update()

        animal_image, _, animal_name = (
            create_animal_image()
        )

        # ----------------------------------------------------
        # Select method
        # ----------------------------------------------------

        if method == "LSB Substitution":

            capacity = lsb_capacity(
                animal_image
            )

            if len(encrypted_data) > capacity:

                raise ValueError(
                    "Message is too large for "
                    "the generated image using LSB."
                )

            status_label.config(
                text=(
                    f"🪄 Hiding message inside "
                    f"{animal_name} using LSB..."
                )
            )

            root.update()

            final_image = lsb_hide_data(
                animal_image,
                encrypted_data
            )

        else:

            capacity = dct_capacity(
                animal_image
            )

            if len(encrypted_data) > capacity:

                raise ValueError(
                    "Message is too large for "
                    "the generated image using DCT."
                )

            status_label.config(
                text=(
                    f"🪄 Hiding message inside "
                    f"{animal_name} using DCT..."
                )
            )

            root.update()

            final_image = dct_hide_data(
                animal_image,
                encrypted_data
            )

        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------

        save_path = filedialog.asksaveasfilename(
            title="Save ENCFRY Image",
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png")
            ],
            initialfile="encfry_image.png"
        )

        if not save_path:

            status_label.config(
                text="Ready"
            )

            return

        final_image.save(
            save_path,
            format="PNG"
        )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        status_label.config(
            text=(
                "✅ ENCFRY image created successfully"
            )
        )

        messagebox.showinfo(
            "ENCFRY",
            f"Message hidden successfully!\n\n"
            f"Animal: {animal_name}\n"
            f"Method: {method}\n\n"
            f"Saved as:\n{save_path}"
        )

    except Exception as error:

        status_label.config(
            text="❌ Error"
        )

        messagebox.showerror(
            "ENCFRY Error",
            str(error)
        )

    finally:

        encrypt_button.config(
            state="normal"
        )


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "ENCFRY — Secure Image Messaging"
)

root.geometry(
    "720x700"
)

root.resizable(
    False,
    False
)

root.configure(
    bg="#f7f3f0"
)


# ============================================================
# HEADER
# ============================================================

tk.Label(
    root,
    text="ENCFRY",
    font=("Segoe UI", 32, "bold"),
    bg="#f7f3f0",
    fg="#3d3430"
).pack(
    pady=(25, 0)
)


tk.Label(
    root,
    text=(
        "Hide a secret message inside "
        "a unique animal image"
    ),
    font=("Segoe UI", 12),
    bg="#f7f3f0",
    fg="#766b66"
).pack(
    pady=(0, 25)
)


# ============================================================
# MESSAGE
# ============================================================

tk.Label(
    root,
    text="Secret Message",
    font=("Segoe UI", 11, "bold"),
    bg="#f7f3f0",
    fg="#3d3430"
).pack(
    anchor="w",
    padx=55
)


message_box = tk.Text(
    root,
    height=7,
    width=66,
    font=("Segoe UI", 11),
    relief="solid",
    borderwidth=1
)

message_box.pack(
    padx=55,
    pady=(5, 18)
)


# ============================================================
# PASSWORD
# ============================================================

tk.Label(
    root,
    text="Password",
    font=("Segoe UI", 11, "bold"),
    bg="#f7f3f0",
    fg="#3d3430"
).pack(
    anchor="w",
    padx=55
)


password_frame = tk.Frame(
    root,
    bg="#f7f3f0"
)

password_frame.pack(
    padx=55,
    pady=(5, 18),
    fill="x"
)


password_entry = tk.Entry(
    password_frame,
    show="•",
    font=("Segoe UI", 11),
    relief="solid",
    borderwidth=1
)

password_entry.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=7
)


show_password_button = tk.Button(
    password_frame,
    text="👁",
    command=toggle_password,
    font=("Segoe UI", 12),
    bg="#ded6d0",
    fg="#3d3430",
    relief="flat",
    width=4,
    cursor="hand2"
)

show_password_button.pack(
    side="left",
    padx=(7, 0)
)


# ============================================================
# STEGANOGRAPHY METHOD
# ============================================================

tk.Label(
    root,
    text="Steganography Method",
    font=("Segoe UI", 11, "bold"),
    bg="#f7f3f0",
    fg="#3d3430"
).pack(
    anchor="w",
    padx=55
)


method_var = tk.StringVar()

method_var.set(
    "LSB Substitution"
)


method_dropdown = ttk.Combobox(
    root,
    textvariable=method_var,
    values=[
        "LSB Substitution",
        "DCT Transform Domain"
    ],
    state="readonly",
    font=("Segoe UI", 11)
)

method_dropdown.pack(
    padx=55,
    pady=(5, 3),
    fill="x"
)

method_dropdown.bind(
    "<<ComboboxSelected>>",
    method_changed
)


method_info = tk.Label(
    root,
    text=(
        "Fast • High capacity • "
        "Pixel-domain steganography"
    ),
    font=("Segoe UI", 9),
    bg="#f7f3f0",
    fg="#8a7e78"
)

method_info.pack(
    pady=(0, 18)
)


# ============================================================
# BUTTON
# ============================================================

encrypt_button = tk.Button(
    root,
    text="🔐  Encrypt & Create Image",
    command=encrypt_and_create,
    font=("Segoe UI", 12, "bold"),
    bg="#5b4b8a",
    fg="white",
    activebackground="#493b72",
    activeforeground="white",
    relief="flat",
    padx=25,
    pady=12,
    cursor="hand2"
)

encrypt_button.pack()


# ============================================================
# STATUS
# ============================================================

status_label = tk.Label(
    root,
    text="Ready",
    font=("Segoe UI", 10),
    bg="#f7f3f0",
    fg="#766b66"
)

status_label.pack(
    pady=18
)


# ============================================================
# FOOTER
# ============================================================

tk.Label(
    root,
    text=(
        "AES-256-GCM  •  LSB / DCT  •  "
        "Random Animal Generation"
    ),
    font=("Segoe UI", 9),
    bg="#f7f3f0",
    fg="#9a908b"
).pack(
    side="bottom",
    pady=15
)


root.mainloop()