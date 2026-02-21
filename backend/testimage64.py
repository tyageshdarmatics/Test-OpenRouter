import base64
import tkinter as tk
from tkinter import filedialog
import os

def select_and_convert_image():
    # Create hidden Tkinter window
    root = tk.Tk()
    root.withdraw()

    # Open file picker
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp"),
            ("All Files", "*.*")
        ]
    )

    if not file_path:
        print("No file selected.")
        return

    # Detect image extension
    file_extension = os.path.splitext(file_path)[1].lower().replace(".", "")
    if file_extension == "jpg":
        file_extension = "jpeg"

    # Convert image to base64
    with open(file_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")

    # Print with proper data URI prefix
    print(f"data:image/{file_extension};base64,{base64_string}")

select_and_convert_image()