import customtkinter as ctk
import hashlib
import hmac
import base64
import os 
import secrets
import string  

from tkinter import filedialog 
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# -----------------------------
# Appearance
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -----------------------------
# Functions
# -----------------------------
  
ALL_BUTTONS = []      
        
def change_theme(choice):

    global CURRENT_THEME
    global ACCENT_COLOR
    global HOVER_COLOR
    global HIGHLIGHT_COLOR

    CURRENT_THEME = choice

    ACCENT_COLOR = COLOR_THEMES[choice]["primary"]
    HOVER_COLOR = COLOR_THEMES[choice]["hover"]
    HIGHLIGHT_COLOR = COLOR_THEMES[choice]["highlight"]

    for button in ALL_BUTTONS:

        button.configure(
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_COLOR
        )

    show_status(f"Theme changed to {choice}")
        
        
def generate_hash():
    text = input_box.get("1.0", "end").strip()

    if not text:
        output_box.configure(state="normal")
        output_box.delete("1.0", "end")
        output_box.configure(state="disabled")
        return

    algo = algorithm.get()

    algorithms = {
        "MD5": hashlib.md5,
        "SHA1": hashlib.sha1,
        "SHA224": hashlib.sha224,
        "SHA256": hashlib.sha256,
        "SHA384": hashlib.sha384,
        "SHA512": hashlib.sha512,
        "BLAKE2B": hashlib.blake2b,
        "BLAKE2S": hashlib.blake2s,
    }

    result = algorithms[algo](text.encode()).hexdigest()

    output_box.configure(state="normal")
    output_box.delete("1.0", "end")
    output_box.insert("1.0", result)
    output_box.configure(state="disabled")
    
def generate_hmac():

    key = key_box.get("1.0", "end").strip()
    message = message_box.get("1.0", "end").strip()

    if not key or not message:
        hmac_output.configure(state="normal")
        hmac_output.delete("1.0", "end")
        hmac_output.configure(state="disabled")
        return

    algo = hmac_algorithm.get()

    algorithms = {
        "MD5": hashlib.md5,
        "SHA1": hashlib.sha1,
        "SHA224": hashlib.sha224,
        "SHA256": hashlib.sha256,
        "SHA384": hashlib.sha384,
        "SHA512": hashlib.sha512,
        "BLAKE2B": hashlib.blake2b,
        "BLAKE2S": hashlib.blake2s,
    }

    result = hmac.new(
        key.encode(),
        message.encode(),
        algorithms[algo]
    ).hexdigest()

    hmac_output.configure(state="normal")
    hmac_output.delete("1.0", "end")
    hmac_output.insert("1.0", result)
    hmac_output.configure(state="disabled")

def toggle_password():

    if password_box.cget("show") == "*":
        password_box.configure(show="")
        eye_btn.configure(text="🙈")

    else:
        password_box.configure(show="*")
        eye_btn.configure(text="👁")
        
def toggle_decrypt_password():

    if decrypt_password_box.cget("show") == "*":
        decrypt_password_box.configure(show="")
        decrypt_eye_btn.configure(text="🙈")
    else:
        decrypt_password_box.configure(show="*")
        decrypt_eye_btn.configure(text="👁")
        
def get_key(password, salt):
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    
    return base64.urlsafe_b64encode(
        kdf.derive(password.encode())
    )

def encrypt_text():

    password = password_box.get()
    text = text_box.get("1.0", "end").strip()

    if not password or not text:
        return

    salt = os.urandom(16)

    key = get_key(password, salt)

    cipher = Fernet(key)

    encrypted = cipher.encrypt(
        text.encode()
    )

    final_data = base64.urlsafe_b64encode(
        salt + encrypted
    ).decode()

    result_box.configure(state="normal")
    result_box.delete("1.0", "end")
    result_box.insert("1.0", final_data)
    result_box.configure(state="disabled")
    
def decrypt_text():

    password = decrypt_password_box.get()

    encrypted_text = encrypted_input_box.get("1.0", "end").strip()

    if not password or not encrypted_text:
        return

    try:

        data = base64.urlsafe_b64decode(encrypted_text)

        salt = data[:16]

        encrypted = data[16:]

        key = get_key(password, salt)

        cipher = Fernet(key)

        decrypted = cipher.decrypt(encrypted)

        decrypted_box.configure(state="normal")
        decrypted_box.delete("1.0", "end")
        decrypted_box.insert("1.0", decrypted.decode())
        decrypted_box.configure(state="disabled")

    except Exception:

        decrypted_box.configure(state="normal")
        decrypted_box.delete("1.0", "end")
        decrypted_box.insert("1.0", "❌ Invalid password or encrypted text.")
        decrypted_box.configure(state="disabled")

def show_status(message):

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return "#{:02X}{:02X}{:02X}".format(*rgb)

    base = hex_to_rgb(HIGHLIGHT_COLOR)

    colors = []

    steps = 20

    for i in range(steps):
        factor = i / (steps - 1)

        r = int(base[0] * (1 - factor))
        g = int(base[1] * (1 - factor))
        b = int(base[2] * (1 - factor))

        colors.append(rgb_to_hex((r, g, b)))

    # Cancel any previous fade animation
    if hasattr(app, "status_after"):
        app.after_cancel(app.status_after)

    status.configure(
        text=message,
        text_color=HIGHLIGHT_COLOR
    )

    def fade(index=0):
        if index < len(colors):
            status.configure(text_color=colors[index])
            app.status_after = app.after(
                30,
                lambda: fade(index + 1)
            )
        else:
            status.configure(text="")
            status.configure(text_color=HIGHLIGHT_COLOR)

    app.status_after = app.after(800, fade)

def clear_boxes():
    input_box.delete("1.0", "end")
    output_box.delete("1.0", "end")
    show_status("Cleared")


def copy_hash():
    result = output_box.get("1.0", "end").strip()

    if result:
        app.clipboard_clear()
        app.clipboard_append(result)
        show_status("Hash copied!")
        
def copy_encrypted():

    app.clipboard_clear()
    app.clipboard_append(
        result_box.get("1.0", "end").strip()
    )

def clear_encrypt():

    password_box.delete(0, "end")

    text_box.delete("1.0", "end")

    result_box.configure(state="normal")
    result_box.delete("1.0", "end")
    result_box.configure(state="disabled")
    
def copy_decrypted():

    app.clipboard_clear()
    app.clipboard_append(
        decrypted_box.get("1.0", "end").strip()
    )

def clear_decrypt():

    decrypt_password_box.delete(0, "end")

    encrypted_input_box.delete("1.0", "end")

    decrypted_box.configure(state="normal")
    decrypted_box.delete("1.0", "end")
    decrypted_box.configure(state="disabled")
    
def update_length(value):

    length_value.configure(
        text=f"Length: {int(value)}"
    )
    
def generate_password():

    characters = ""

    if uppercase_var.get():
        characters += string.ascii_uppercase

    if lowercase_var.get():
        characters += string.ascii_lowercase

    if numbers_var.get():
        characters += string.digits

    if symbols_var.get():
        characters += string.punctuation

    if exclude_similar_var.get():

        similar = "0OoIl1"

        characters = "".join(
            c for c in characters if c not in similar
        )

    if not characters:

        password_output.configure(state="normal")
        password_output.delete("1.0", "end")
        password_output.insert("1.0", "Please select at least one option.")
        password_output.configure(state="disabled")
        return

    length = int(length_slider.get())

    password = "".join(
        secrets.choice(characters)
        for _ in range(length)
    )

    password_output.configure(state="normal")
    password_output.delete("1.0", "end")
    password_output.insert("1.0", password)
    password_output.configure(state="disabled")
    update_strength()

def compare_hashes():

    hash1 = hash1_box.get("1.0", "end").strip().lower()
    hash2 = hash2_box.get("1.0", "end").strip().lower()

    if not hash1 or not hash2:
        compare_result.configure(text="")
        return

    if hash1 == hash2:
        compare_result.configure(
            text="✅ Hashes Match"
        )
    else:
        compare_result.configure(
            text="❌ Hashes Do Not Match"
        )
        
def update_strength():

    score = 0

    length = int(length_slider.get())

    if length >= 8:
        score += 1

    if length >= 12:
        score += 1

    if uppercase_var.get():
        score += 1

    if lowercase_var.get():
        score += 1

    if numbers_var.get():
        score += 1

    if symbols_var.get():
        score += 1

    strength_bar.set(score / 6)

    if score <= 2:
        strength_bar.configure(progress_color="#E53935")   # Red
        strength_label.configure(text=" Weak")

    elif score <= 4:
        strength_bar.configure(progress_color="#FB8C00")   # Orange
        strength_label.configure(text=" Medium")

    elif score == 5:
        strength_bar.configure(progress_color="#7CB342")   # Light Green
        strength_label.configure(text=" Strong")

    else:
        strength_bar.configure(progress_color="#00C853")   # Bright Green
        strength_label.configure(text=" Very Strong")
        
def paste_encrypted():

    try:
        text = app.clipboard_get()

        encrypted_input_box.delete("1.0", "end")
        encrypted_input_box.insert("1.0", text)

    except:
        pass
    
def create_button(parent, **kwargs):
    btn = ctk.CTkButton(
        parent,
        fg_color=ACCENT_COLOR,
        hover_color=HOVER_COLOR,
        height=BUTTON_HEIGHT,
        corner_radius=BUTTON_RADIUS,
        font=TEXT_FONT,
        **kwargs
    )

    ALL_BUTTONS.append(btn)

    return btn

# -----------------------------
# Main Window
# -----------------------------
app = ctk.CTk()
app.title("Crypto Toolkit")
app.geometry("1000x700")
app.minsize(950, 650)
app.update_idletasks()

width = 1000
height = 700

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

x = (screen_width // 2) - (width // 2)
y = (screen_height // 2) - (height // 2)

app.geometry(f"{width}x{height}+{x}+{y}")

# ======================================================
# DESIGN SYSTEM
# ======================================================

TITLE_FONT = ("Segoe UI", 24, "bold")
HEADER_FONT = ("Segoe UI", 18, "bold")
LABEL_FONT = ("Segoe UI", 14, "bold")
TEXT_FONT = ("Segoe UI", 13)

# ==========================
# COLOR PALETTES
# ==========================

COLOR_THEMES = {
    "Midnight Opulence": {
        "primary": "#0F3460",
        "hover": "#16213E",
        "highlight": "#EFC07B"
    },

    "Golden Hour Elite": {
        "primary": "#E6D17B",
        "hover": "#F1E49A",
        "highlight": "#2C1810"
    },

    "Emerald Sophistication": {
        "primary": "#2D5A4A",
        "hover": "#0D4C3C",
        "highlight": "#7BA05B"
    },

    "Platinum Prestige": {
        "primary": "#34495E",
        "hover": "#2C3E50",
        "highlight": "#BDC3C7"
    },

    "Royal Burgundy": {
        "primary": "#8B1538",
        "hover": "#722F37",
        "highlight": "#A0522D"
    },

    "Rose Gold": {
        "primary": "#B76E79",
        "hover": "#E8B4B8",
        "highlight": "#F7E7CE"
    },

    "Obsidian Elegance": {
        "primary": "#2C2C2C",
        "hover": "#0C0C0C",
        "highlight": "#BEA98E"
    },

    "Arctic Luxury": {
        "primary": "#B0C4DE",
        "hover": "#E6E6FA",
        "highlight": "#2F4F4F"
    }
}

CURRENT_THEME = "Midnight Opulence"

ACCENT_COLOR = COLOR_THEMES[CURRENT_THEME]["primary"]
HOVER_COLOR = COLOR_THEMES[CURRENT_THEME]["hover"]
HIGHLIGHT_COLOR = COLOR_THEMES[CURRENT_THEME]["highlight"]

#------------------------------------------
#------------------------------------------

BUTTON_HEIGHT = 42
BUTTON_RADIUS = 10
BUTTON_WIDTH = 150

TEXTBOX_HEIGHT = 120

ENTRY_HEIGHT = 35

PAD_X = 20
PAD_Y = 10
SECTION_PADY = (20, 8)

# -----------------------------
# Title
# -----------------------------
title = ctk.CTkLabel(
    app,
    text="🔐 Crypto Toolkit",
    font=TITLE_FONT
)
title.pack(pady=20)

# -----------------------------
# Tabs
# -----------------------------
tabs = ctk.CTkTabview(app)
tabs.pack(fill="both", expand=True, padx=20, pady=10)

tabs.add("Hash")
tabs.add("File Hash")
tabs.add("HMAC")
tabs.add("Encrypt")
tabs.add("Decrypt")
tabs.add("Password")
tabs.add("Compare")
tabs.add("About")

# =====================================
# PASSWORD TAB
# =====================================

password_tab = tabs.tab("Password")

length_label = ctk.CTkLabel(
    password_tab,
    text="Password Length",
    font=LABEL_FONT
)

length_label.pack(pady=(20, 5))

length_slider = ctk.CTkSlider(
    password_tab,
    from_=4,
    to=64,
    number_of_steps=60
)

length_slider.set(16)
length_slider.pack(fill="x", padx=20)

length_slider.configure(
    command=lambda value: (
        update_length(value),
        update_strength()
    )
)

length_value = ctk.CTkLabel(
    password_tab,
    text="Length: 16",
    font=TEXT_FONT
)

length_value.pack(pady=(5, 15))

uppercase_var = ctk.BooleanVar(value=True)
lowercase_var = ctk.BooleanVar(value=True)
numbers_var = ctk.BooleanVar(value=True)
symbols_var = ctk.BooleanVar(value=True)
exclude_similar_var = ctk.BooleanVar(value=False)

uppercase_cb = ctk.CTkCheckBox(
    password_tab,
    text="Uppercase Letters (A-Z)",
    variable=uppercase_var
)
uppercase_cb.pack(anchor="w", padx=20)

lowercase_cb = ctk.CTkCheckBox(
    password_tab,
    text="Lowercase Letters (a-z)",
    variable=lowercase_var
)
lowercase_cb.pack(anchor="w", padx=20)

numbers_cb = ctk.CTkCheckBox(
    password_tab,
    text="Numbers (0-9)",
    variable=numbers_var
)
numbers_cb.pack(anchor="w", padx=20)

symbols_cb = ctk.CTkCheckBox(
    password_tab,
    text="Symbols (!@#$%^&*)",
    variable=symbols_var
)
symbols_cb.pack(anchor="w", padx=20)

exclude_cb = ctk.CTkCheckBox(
    password_tab,
    text="Exclude Similar Characters (0 O o I l 1)",
    variable=exclude_similar_var
)
exclude_cb.pack(anchor="w", padx=20, pady=(0, 20))

uppercase_cb.configure(command=update_strength)
lowercase_cb.configure(command=update_strength)
numbers_cb.configure(command=update_strength)
symbols_cb.configure(command=update_strength)
exclude_cb.configure(command=update_strength)

generate_password_btn = create_button(
    password_tab,
    text="🔑 Generate Password",
    command=generate_password
)

generate_password_btn.pack(fill="x", padx=20, pady=(0, 20))

password_output_label = ctk.CTkLabel(
    password_tab,
    text="Generated Password",
    font=LABEL_FONT
)
password_output_label.pack()

password_output = ctk.CTkTextbox(
    password_tab,
    height=60
)
password_output.pack(fill="x", padx=20, pady=(5, 15))

strength_bar = ctk.CTkProgressBar(
    password_tab,
    height=12
)

strength_bar.pack(fill="x", padx=20)

strength_bar.set(0)

strength_label = ctk.CTkLabel(
    password_tab,
    text="Strength: -",
    font=LABEL_FONT
)

strength_label.pack(pady=(8, 15))

password_output.configure(state="disabled")

password_button_frame = ctk.CTkFrame(
    password_tab,
    fg_color="transparent"
)
password_button_frame.pack(fill="x", padx=20)

copy_password_btn = create_button(
    password_button_frame,
    text="📋 Copy"
)

copy_password_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))

clear_password_btn = create_button(
    password_button_frame,
    text="🗑 Clear"
)
clear_password_btn.pack(side="left", expand=True, fill="x", padx=(10, 0))

# =====================================
# HASH COMPARISON TAB
# =====================================

compare_tab = tabs.tab("Compare")

# Hash 1
hash1_label = ctk.CTkLabel(
    compare_tab,
    text="Hash 1",
    font=LABEL_FONT
)
hash1_label.pack(pady=(20,5))

hash1_box = ctk.CTkTextbox(
    compare_tab,
    height=80
)
hash1_box.pack(fill="x", padx=20)

hash1_box.bind("<KeyRelease>", lambda event: compare_hashes())

# Hash 2
hash2_label = ctk.CTkLabel(
    compare_tab,
    text="Hash 2",
    font=LABEL_FONT
)
hash2_label.pack(pady=(20,5))

hash2_box = ctk.CTkTextbox(
    compare_tab,
    height=80
)
hash2_box.pack(fill="x", padx=20)

hash2_box.bind("<KeyRelease>", lambda event: compare_hashes())

# Result
compare_result = ctk.CTkLabel(
    compare_tab,
    text="",
    font=LABEL_FONT
)

compare_result.pack(pady=10)

# =====================================
# ABOUT TAB
# =====================================

about_tab = tabs.tab("About")

title_label = ctk.CTkLabel(
    about_tab,
    text="Crypto Toolkit",
    font=TITLE_FONT
)
title_label.pack(pady=(25, 5))

version_title = ctk.CTkLabel(
    about_tab,
    text="Version",
    font=LABEL_FONT
)
version_title.pack()

version_label = ctk.CTkLabel(
    about_tab,
    text="v1.0.0",
    font=LABEL_FONT
)
version_label.pack(pady=(0, 20))

developer_title = ctk.CTkLabel(
    about_tab,
    text="Developer",
    font=LABEL_FONT
)
developer_title.pack()

developer_label = ctk.CTkLabel(
    about_tab,
    text="© 2026 Baman Jinith",
    font=LABEL_FONT
)
developer_label.pack(pady=(0, 20))

appearance_title = ctk.CTkLabel(
    about_tab,
    text="Appearance",
    font=LABEL_FONT
)
appearance_title.pack()

appearance_menu = ctk.CTkOptionMenu(
    about_tab,
    values=["Dark", "Light"],
    width=180,
    command=ctk.set_appearance_mode
)

appearance_menu.set("Dark")
appearance_menu.pack(pady=(5, 25))

theme_title = ctk.CTkLabel(
    about_tab,
    text="Accent Theme",
    font=LABEL_FONT
)
theme_title.pack()

theme_menu = ctk.CTkOptionMenu(
    about_tab,
    values=list(COLOR_THEMES.keys()),
    command=change_theme,
    width=180
)

theme_menu.set("Midnight Opulence")
theme_menu.pack(pady=(5, 20))

# ==========================
# Keyboard Shortcuts
# ==========================

shortcuts_title = ctk.CTkLabel(
    about_tab,
    text="Keyboard Shortcuts",
    font=HEADER_FONT
)
shortcuts_title.pack(pady=(10, 10))

shortcuts_box = ctk.CTkTextbox(
    about_tab,
    width=420,
    height=150,
    font=TEXT_FONT
)
shortcuts_box.pack()

shortcuts_box.insert("1.0",
"""Shortcut              Action

Ctrl + C              Copy Result

Ctrl + V              Paste Text
""")

shortcuts_box.configure(state="disabled")

# -------------------------------------------
# -------------------------------------------

footer = ctk.CTkLabel(
    about_tab,
    text="Built with Python & CustomTkinter",
    font=TEXT_FONT
)
footer.pack(side="bottom", pady=20)


# -----------------------------
# Status Bar
# -----------------------------
footer = ctk.CTkFrame(app, fg_color="transparent")
footer.pack(fill="x", padx=10, pady=8)

status = ctk.CTkLabel(
    footer,
    text="",
    font=TEXT_FONT,
    text_color="#66d9ef"
)
status.pack(side="left")

copyright = ctk.CTkLabel(
    footer,
    text="© 2026 Baman Jinith",
    font=TEXT_FONT,
    text_color="gray60"
)
copyright.pack(side="right")
# =============================
# HASH TAB
# =============================

hash_tab = tabs.tab("Hash")

algo_label = ctk.CTkLabel(
    hash_tab,
    text="Algorithm",
    font=LABEL_FONT
)

algo_label.pack(pady=(20, 5))

algorithm = ctk.CTkOptionMenu(
    hash_tab,
    values=[
        "MD5",
        "SHA1",
        "SHA224",
        "SHA256",
        "SHA384",
        "SHA512",
        "BLAKE2B",
        "BLAKE2S"
    ],
    width=200
)
algorithm.set("SHA256")
algorithm.pack()

algorithm.configure(command=lambda choice: generate_hash())

input_label = ctk.CTkLabel(
    hash_tab,
    text="Input",
    font=LABEL_FONT
)
input_label.pack(pady=(20, 5))

input_box = ctk.CTkTextbox(hash_tab, height=120)
input_box.pack(fill="x", padx=20)

input_box.bind("<KeyRelease>", lambda event: generate_hash())

output_label = ctk.CTkLabel(
    hash_tab,
    text="Hash",
    font=LABEL_FONT
)
output_label.pack(pady=(20, 5))

output_box = ctk.CTkTextbox(hash_tab, height=120)
output_box.pack(fill="x", padx=20, pady=(0, 10))

output_box.configure(state="disabled")

# =====================================
# FILE HASH TAB
# =====================================

file_tab = tabs.tab("File Hash")

# File Label
file_label = ctk.CTkLabel(
    file_tab,
    text="Selected File",
    font=LABEL_FONT
)
file_label.pack(pady=(20, 5))

# File path display
file_path = ctk.CTkEntry(
    file_tab,
    width=700
)
file_path.pack(padx=20, fill="x")

# Browse Button
def browse_file():
    filename = filedialog.askopenfilename()

    if not filename:
        return

    file_path.delete(0, "end")
    file_path.insert(0, filename)

    algo = file_algorithm.get()

    algorithms = {
        "MD5": hashlib.md5,
        "SHA1": hashlib.sha1,
        "SHA224": hashlib.sha224,
        "SHA256": hashlib.sha256,
        "SHA384": hashlib.sha384,
        "SHA512": hashlib.sha512,
        "BLAKE2B": hashlib.blake2b,
        "BLAKE2S": hashlib.blake2s,
    }

    hasher = algorithms[algo]()

    with open(filename, "rb") as file:
        while True:
            chunk = file.read(8192)

            if not chunk:
                break

            hasher.update(chunk)

    result = hasher.hexdigest()

    file_output.configure(state="normal")
    file_output.delete("1.0", "end")
    file_output.insert("1.0", result)
    file_output.configure(state="disabled")
    
browse_btn = create_button(
    file_tab,
    text="📂 Browse",
    command=browse_file
)
browse_btn.pack(pady=15)

# =====================================
# HMAC TAB
# =====================================

hmac_tab = tabs.tab("HMAC")

# Algorithm
hmac_algo_label = ctk.CTkLabel(
    hmac_tab,
    text="Algorithm",
    font=LABEL_FONT
)
hmac_algo_label.pack(pady=(20, 5))

hmac_algorithm = ctk.CTkOptionMenu(
    hmac_tab,
    values=[
        "MD5",
        "SHA1",
        "SHA224",
        "SHA256",
        "SHA384",
        "SHA512",
        "BLAKE2B",
        "BLAKE2S"
    ],
    width=200
)

hmac_algorithm.set("SHA256")
hmac_algorithm.pack()

hmac_algorithm.configure(command=lambda choice: generate_hmac())

# Secret Key
key_label = ctk.CTkLabel(
    hmac_tab,
    text="Secret Key",
    font=LABEL_FONT
)
key_label.pack(pady=(20, 5))

key_box = ctk.CTkTextbox(hmac_tab, height=80)
key_box.pack(fill="x", padx=20)

key_box.bind("<KeyRelease>", lambda event: generate_hmac())

# Message
message_label = ctk.CTkLabel(
    hmac_tab,
    text="Message",
    font=LABEL_FONT
)
message_label.pack(pady=(20, 5))

message_box = ctk.CTkTextbox(hmac_tab, height=120)
message_box.pack(fill="x", padx=20)

message_box.bind("<KeyRelease>", lambda event: generate_hmac())

# Output
hmac_output_label = ctk.CTkLabel(
    hmac_tab,
    text="HMAC",
    font=LABEL_FONT
)
hmac_output_label.pack(pady=(20, 5))

hmac_output = ctk.CTkTextbox(hmac_tab, height=100)
hmac_output.pack(fill="x", padx=20)

hmac_output.configure(state="disabled")

# Algorithm Label
file_algo_label = ctk.CTkLabel(
    file_tab,
    text="Algorithm",
    font=LABEL_FONT
)
file_algo_label.pack(pady=(10, 5))

# Algorithm dropdown
file_algorithm = ctk.CTkOptionMenu(
    file_tab,
    values=[
        "MD5",
        "SHA1",
        "SHA224",
        "SHA256",
        "SHA384",
        "SHA512",
        "BLAKE2B",
        "BLAKE2S"
    ],
    width=200
)

file_algorithm.set("SHA256")
file_algorithm.pack()

file_algorithm.configure(command=lambda choice: browse_file())

# Hash Label
file_hash_label = ctk.CTkLabel(
    file_tab,
    text="Hash",
    font=LABEL_FONT
)

file_hash_label.pack(pady=(20, 5))

# Output
file_output = ctk.CTkTextbox(file_tab, height=100)
file_output.pack(fill="x", padx=20)

file_output.configure(state="disabled")

# =====================================
# ENCRYPTION TAB
# =====================================

encrypt_tab = tabs.tab("Encrypt")

# Password
password_label = ctk.CTkLabel(
    encrypt_tab,
    text="Password",
    font=LABEL_FONT
)
password_label.pack(pady=(20, 5))

password_frame = ctk.CTkFrame(
    encrypt_tab,
    fg_color="transparent"
)
password_frame.pack(fill="x", padx=20)

password_box = ctk.CTkEntry(
    password_frame,
    show="*"
)
password_box.pack(side="left", fill="x", expand=True)

eye_btn = create_button(
    password_frame,
    text="👁",
    command=lambda: toggle_password()
)

eye_btn.pack(side="right", padx=(10, 0))

# Text
text_label = ctk.CTkLabel(
    encrypt_tab,
    text="Text",
    font=LABEL_FONT
)
text_label.pack(pady=(20, 5))

text_box = ctk.CTkTextbox(
    encrypt_tab,
    height=140
)
text_box.pack(fill="x", padx=20)

# Buttons
button_frame = ctk.CTkFrame(
    encrypt_tab,
    fg_color="transparent"
)
button_frame.pack(fill="x", padx=20, pady=20)

encrypt_btn = create_button(
    button_frame,
    text="🔒 Encrypt",
    command=encrypt_text
)
encrypt_btn.pack(fill="x", expand=True)

# Result
result_label = ctk.CTkLabel(
    encrypt_tab,
    text="Result",
    font=LABEL_FONT
)
result_label.pack(pady=(10, 5))

result_box = ctk.CTkTextbox(
    encrypt_tab,
    height=140
)
result_box.pack(fill="x", padx=20)

encrypt_button_frame = ctk.CTkFrame(
    encrypt_tab,
    fg_color="transparent"
)
encrypt_button_frame.pack(pady=10)

copy_encrypt_btn = create_button(
    encrypt_button_frame,
    text="📋 Copy",
    command=copy_encrypted
)
copy_encrypt_btn.pack(side="left", padx=10)

clear_encrypt_btn = create_button(
    encrypt_button_frame,
    text="🗑 Clear",
    command=clear_encrypt
)
clear_encrypt_btn.pack(side="left", padx=10)

result_box.configure(state="disabled")


# =====================================
# DECRYPT TAB
# =====================================

decrypt_tab = tabs.tab("Decrypt")

# Password
decrypt_password_label = ctk.CTkLabel(
    decrypt_tab,
    text="Password",
    font=LABEL_FONT
)
decrypt_password_label.pack(pady=(20, 5))

decrypt_password_frame = ctk.CTkFrame(
    decrypt_tab,
    fg_color="transparent"
)
decrypt_password_frame.pack(fill="x", padx=20)

decrypt_password_box = ctk.CTkEntry(
    decrypt_password_frame,
    show="*"
)
decrypt_password_box.pack(side="left", fill="x", expand=True)

decrypt_eye_btn = create_button(
    decrypt_password_frame,
    text="👁",
    command=toggle_decrypt_password
)
decrypt_eye_btn.pack(side="right", padx=(10, 0))

# Encrypted Text
encrypted_input_label = ctk.CTkLabel(
    decrypt_tab,
    text="Encrypted Text",
    font=LABEL_FONT
)
encrypted_input_label.pack(pady=(20, 5))

encrypted_input_box = ctk.CTkTextbox(
    decrypt_tab,
    height=140
)
encrypted_input_box.pack(fill="x", padx=20)

# Decrypt Button
decrypt_btn = create_button(
    decrypt_tab,
    text="🔓 Decrypt",
    command=decrypt_text
)
decrypt_btn.pack(fill="x", padx=20, pady=20)

# Plain Text
decrypted_label = ctk.CTkLabel(
    decrypt_tab,
    text="Plain Text",
    font=LABEL_FONT
)
decrypted_label.pack(pady=(10, 5))

decrypted_box = ctk.CTkTextbox(
    decrypt_tab,
    height=140
)
decrypted_box.pack(fill="x", padx=20)

decrypt_button_frame = ctk.CTkFrame(
    decrypt_tab,
    fg_color="transparent"
)
decrypt_button_frame.pack(pady=10)

paste_btn = create_button(
    decrypt_button_frame,
    text="📋 Paste",
    command=paste_encrypted
)

paste_btn.pack(
    side="left",
    expand=True,
    fill="x",
    padx=(0, 10)
)

copy_decrypt_btn = create_button(
    decrypt_button_frame,
    text="📋 Copy",
    command=copy_decrypted
)

copy_decrypt_btn.pack(side="left", padx=10)

clear_decrypt_btn = create_button(
    decrypt_button_frame,
    text="🗑 Clear",
    command=clear_decrypt
)

clear_decrypt_btn.pack(side="left", padx=10)

decrypted_box.configure(state="disabled")


# -----------------------------
# HashButtons
# -----------------------------
button_frame = ctk.CTkFrame(hash_tab, fg_color="transparent")
button_frame.pack(pady=10)

copy_btn = create_button(
    button_frame,
    text="Copy",
    command=copy_hash
)

copy_btn.pack(side="left", padx=10)

clear_btn = create_button(
    button_frame,
    text="Clear",
    command=clear_boxes
)

clear_btn.pack(side="left", padx=10)

input_box.bind("<KeyRelease>", lambda event: generate_hash())


# -----------------------------
# Run
# -----------------------------
app.mainloop()