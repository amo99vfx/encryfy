import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

from PIL import Image

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from image_codec import extract_data as extract_lsb
from dct_codec import extract_data as extract_dct


# ============================================================
# ENCRYPTION SETTINGS
# ============================================================

PBKDF2_ITERATIONS = 600_000
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32


# ============================================================
# WINDOWS TEXT-TO-SPEECH
# ============================================================

tts_process = None


def speak_message():

    global tts_process

    message = recovered_text.get(
        "1.0",
        tk.END
    ).strip()

    if not message:

        messagebox.showwarning(
            "No Message",
            "There is no recovered message to speak."
        )

        return

    try:

        stop_speaking()

        status_label.config(
            text="🔊 Speaking message..."
        )

        root.update()

        safe_message = message.replace(
            "'",
            "''"
        )

        powershell_command = f"""
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.Rate = 0
$speaker.Volume = 100
$speaker.Speak('{safe_message}')
"""

        tts_process = subprocess.Popen(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                powershell_command
            ],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        root.after(
            500,
            check_speech_status
        )

    except Exception as error:

        messagebox.showerror(
            "Speech Error",
            str(error)
        )


def check_speech_status():

    global tts_process

    if tts_process is not None:

        if tts_process.poll() is None:

            root.after(
                500,
                check_speech_status
            )

        else:

            tts_process = None

            status_label.config(
                text="✓ Finished speaking"
            )


def stop_speaking():

    global tts_process

    if tts_process is not None:

        try:
            tts_process.terminate()
        except Exception:
            pass

        tts_process = None


# ============================================================
# IMAGE SELECTION
# ============================================================

selected_image_path = None


def browse_image():

    global selected_image_path

    path = filedialog.askopenfilename(
        title="Select ENCFRY Image",
        filetypes=[
            ("PNG Images", "*.png"),
            ("All Images", "*.*")
        ]
    )

    if not path:
        return

    selected_image_path = path

    image_label.config(
        text=(
            f"Selected:\n"
            f"{os.path.basename(path)}"
        )
    )

    recovered_text.delete(
        "1.0",
        tk.END
    )

    play_button.config(
        state=tk.DISABLED
    )

    stop_button.config(
        state=tk.DISABLED
    )

    status_label.config(
        text="✓ ENCFRY image selected"
    )


# ============================================================
# PASSWORD SHOW / HIDE
# ============================================================

def toggle_password():

    if password_entry.cget("show") == "*":

        password_entry.config(
            show=""
        )

        password_toggle.config(
            text="🙈"
        )

    else:

        password_entry.config(
            show="*"
        )

        password_toggle.config(
            text="👁"
        )


# ============================================================
# TRY LSB / DCT
# ============================================================

def extract_encfry_data(image):

    # --------------------------------------------------------
    # Try LSB first
    # --------------------------------------------------------

    try:

        data = extract_lsb(
            image
        )

        return data, "LSB Substitution"

    except Exception:
        pass

    # --------------------------------------------------------
    # Try DCT
    # --------------------------------------------------------

    try:

        data = extract_dct(
            image
        )

        return data, "DCT Transform Domain"

    except Exception:
        pass

    raise ValueError(
        "This image does not contain "
        "valid ENCFRY data."
    )


# ============================================================
# DECODE MESSAGE
# ============================================================

def decode_message():

    if not selected_image_path:

        messagebox.showwarning(
            "No Image",
            "Please select an ENCFRY PNG image first."
        )

        return

    password = password_entry.get()

    if not password:

        messagebox.showwarning(
            "No Password",
            "Please enter the password."
        )

        return

    try:

        status_label.config(
            text="🔍 Detecting steganography method..."
        )

        root.update()

        # ----------------------------------------------------
        # Open image
        # ----------------------------------------------------

        image = Image.open(
            selected_image_path
        ).convert("RGB")

        # ----------------------------------------------------
        # Automatically detect method
        # ----------------------------------------------------

        encrypted_data, method = (
            extract_encfry_data(
                image
            )
        )

        status_label.config(
            text=f"✓ Detected: {method}"
        )

        root.update()

        # ----------------------------------------------------
        # Validate encrypted payload
        # ----------------------------------------------------

        if len(encrypted_data) < (
            SALT_SIZE + NONCE_SIZE
        ):

            raise ValueError(
                "Invalid encrypted ENCFRY data."
            )

        # ----------------------------------------------------
        # Extract salt
        # ----------------------------------------------------

        salt = encrypted_data[
            :SALT_SIZE
        ]

        # ----------------------------------------------------
        # Extract nonce
        # ----------------------------------------------------

        nonce = encrypted_data[
            SALT_SIZE:
            SALT_SIZE + NONCE_SIZE
        ]

        # ----------------------------------------------------
        # Extract ciphertext
        # ----------------------------------------------------

        ciphertext = encrypted_data[
            SALT_SIZE + NONCE_SIZE:
        ]

        # ----------------------------------------------------
        # Derive AES key
        # ----------------------------------------------------

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_SIZE,
            salt=salt,
            iterations=PBKDF2_ITERATIONS
        )

        key = kdf.derive(
            password.encode("utf-8")
        )

        # ----------------------------------------------------
        # AES-256-GCM
        # ----------------------------------------------------

        aes = AESGCM(
            key
        )

        decrypted = aes.decrypt(
            nonce,
            ciphertext,
            None
        )

        # ----------------------------------------------------
        # Convert to text
        # ----------------------------------------------------

        message = decrypted.decode(
            "utf-8"
        )

        # ----------------------------------------------------
        # Display message
        # ----------------------------------------------------

        recovered_text.delete(
            "1.0",
            tk.END
        )

        recovered_text.insert(
            "1.0",
            message
        )

        # ----------------------------------------------------
        # Enable audio
        # ----------------------------------------------------

        play_button.config(
            state=tk.NORMAL
        )

        stop_button.config(
            state=tk.NORMAL
        )

        status_label.config(
            text=(
                f"✓ Decrypted successfully "
                f"using {method}"
            )
        )

        messagebox.showinfo(
            "ENCFRY",
            f"Message successfully decrypted!\n\n"
            f"Method detected: {method}"
        )

    except Exception as error:

        recovered_text.delete(
            "1.0",
            tk.END
        )

        play_button.config(
            state=tk.DISABLED
        )

        stop_button.config(
            state=tk.DISABLED
        )

        status_label.config(
            text="❌ Could not decrypt message"
        )

        messagebox.showerror(
            "Decryption Failed",
            "Could not decrypt the message.\n\n"
            "Possible reasons:\n"
            "• Wrong password\n"
            "• Invalid ENCFRY image\n"
            "• Image was modified\n"
            "• Image was converted from PNG\n\n"
            f"Technical details:\n{error}"
        )


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "ENCFRY — Secure Message Reader"
)

root.geometry(
    "720x760"
)

root.resizable(
    True,
    True
)

root.configure(
    bg="#f5f5f5"
)


# ============================================================
# SCROLLABLE AREA
# ============================================================

container = tk.Frame(
    root,
    bg="#f5f5f5"
)

container.pack(
    fill="both",
    expand=True
)


canvas = tk.Canvas(
    container,
    bg="#f5f5f5",
    highlightthickness=0
)

scrollbar = tk.Scrollbar(
    container,
    orient="vertical",
    command=canvas.yview
)

scrollable_frame = tk.Frame(
    canvas,
    bg="#f5f5f5"
)

scrollable_frame.bind(
    "<Configure>",
    lambda event: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas_window = canvas.create_window(
    (0, 0),
    window=scrollable_frame,
    anchor="nw"
)

canvas.configure(
    yscrollcommand=scrollbar.set
)

canvas.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)


def resize_frame(event):

    canvas.itemconfig(
        canvas_window,
        width=event.width
    )


canvas.bind(
    "<Configure>",
    resize_frame
)


def mousewheel(event):

    canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


canvas.bind_all(
    "<MouseWheel>",
    mousewheel
)


# ============================================================
# HEADER
# ============================================================

tk.Label(
    scrollable_frame,
    text="ENCFRY",
    font=("Segoe UI", 30, "bold"),
    bg="#f5f5f5",
    fg="#222222"
).pack(
    pady=(25, 5)
)


tk.Label(
    scrollable_frame,
    text="Decrypt • Recover • Listen",
    font=("Segoe UI", 13),
    bg="#f5f5f5",
    fg="#666666"
).pack(
    pady=(0, 25)
)


# ============================================================
# IMAGE
# ============================================================

image_frame = tk.Frame(
    scrollable_frame,
    bg="white",
    bd=1,
    relief="solid"
)

image_frame.pack(
    padx=40,
    fill="x"
)


image_label = tk.Label(
    image_frame,
    text="No ENCFRY image selected",
    font=("Segoe UI", 11),
    bg="white",
    fg="#777777",
    height=4
)

image_label.pack(
    padx=20,
    pady=15
)


browse_button = tk.Button(
    image_frame,
    text="📂 Browse ENCFRY Image",
    font=("Segoe UI", 11, "bold"),
    command=browse_image,
    padx=20,
    pady=8,
    cursor="hand2"
)

browse_button.pack(
    pady=(0, 15)
)


# ============================================================
# PASSWORD
# ============================================================

password_frame = tk.Frame(
    scrollable_frame,
    bg="#f5f5f5"
)

password_frame.pack(
    padx=40,
    pady=25,
    fill="x"
)


tk.Label(
    password_frame,
    text="🔑 Password",
    font=("Segoe UI", 11, "bold"),
    bg="#f5f5f5"
).pack(
    anchor="w"
)


password_row = tk.Frame(
    password_frame,
    bg="#f5f5f5"
)

password_row.pack(
    fill="x",
    pady=(7, 0)
)


password_entry = tk.Entry(
    password_row,
    font=("Segoe UI", 12),
    show="*",
    bd=1,
    relief="solid"
)

password_entry.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=7
)


password_toggle = tk.Button(
    password_row,
    text="👁",
    font=("Segoe UI", 11),
    command=toggle_password,
    width=4,
    cursor="hand2"
)

password_toggle.pack(
    side="left",
    padx=(7, 0)
)


# ============================================================
# DECODE
# ============================================================

decode_button = tk.Button(
    scrollable_frame,
    text="🔓 Decode Message",
    font=("Segoe UI", 13, "bold"),
    command=decode_message,
    padx=30,
    pady=12,
    cursor="hand2"
)

decode_button.pack(
    pady=(0, 25)
)


# ============================================================
# RECOVERED MESSAGE
# ============================================================

tk.Label(
    scrollable_frame,
    text="🔓 Recovered Message",
    font=("Segoe UI", 12, "bold"),
    bg="#f5f5f5"
).pack(
    anchor="w",
    padx=40
)


recovered_text = tk.Text(
    scrollable_frame,
    height=7,
    width=70,
    font=("Segoe UI", 11),
    wrap="word",
    bd=1,
    relief="solid"
)

recovered_text.pack(
    padx=40,
    pady=(7, 15)
)


# ============================================================
# AUDIO
# ============================================================

speech_frame = tk.Frame(
    scrollable_frame,
    bg="#f5f5f5"
)

speech_frame.pack(
    pady=(0, 20)
)


play_button = tk.Button(
    speech_frame,
    text="🔊 Play Message",
    font=("Segoe UI", 11, "bold"),
    command=speak_message,
    state=tk.DISABLED,
    padx=20,
    pady=9,
    cursor="hand2"
)

play_button.pack(
    side="left",
    padx=5
)


stop_button = tk.Button(
    speech_frame,
    text="⏹ Stop",
    font=("Segoe UI", 11, "bold"),
    command=stop_speaking,
    state=tk.DISABLED,
    padx=20,
    pady=9,
    cursor="hand2"
)

stop_button.pack(
    side="left",
    padx=5
)


# ============================================================
# STATUS
# ============================================================

status_label = tk.Label(
    scrollable_frame,
    text="Ready",
    font=("Segoe UI", 10),
    bg="#f5f5f5",
    fg="#666666"
)

status_label.pack(
    pady=(0, 10)
)


# ============================================================
# FOOTER
# ============================================================

tk.Label(
    scrollable_frame,
    text=(
        "AES-256-GCM  •  LSB / DCT  •  "
        "Text-to-Speech"
    ),
    font=("Segoe UI", 9),
    bg="#f5f5f5",
    fg="#999999"
).pack(
    pady=(0, 25)
)


# ============================================================
# START
# ============================================================

root.mainloop()