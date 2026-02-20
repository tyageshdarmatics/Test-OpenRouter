import os
import requests
import json

# ==============================
# CONFIG
# ==============================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Set in environment
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "nvidia/nemotron-nano-12b-v2-vl:free"

if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not set in environment variables")


# ==============================
# REQUEST HEADERS
# ==============================

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Dermatology Skin Analyzer"
}


# ==============================
# PROMPT
# ==============================

analysis_prompt = """
You are an expert dermatologist. Analyze these facial images VERY CAREFULLY and detect ALL visible skin conditions.
    
        **CRITICAL INSTRUCTIONS:**
        1. Look at EVERY visible area of the skin - forehead, cheeks, nose, chin, temples, jaw.
        2. Detect EVERYTHING visible - even minor issues count.
        3. Do NOT skip or miss any visible skin problems.
        4. Provide accurate bounding boxes for EVERY condition you detect.
        
        **Conditions to look for (be thorough):**
        - Acne, pustules, comedones, whiteheads, blackheads, pimples
        - Redness, inflammation, irritation, rosacea
        - Wrinkles, fine lines, crow's feet, forehead lines
        - Dark circles, under-eye bags, puffiness
        - Dark spots, hyperpigmentation, sun spots, melasma
        - Texture issues, rough patches, bumps, enlarged pores
        - Dryness, flakiness, dehydration, dry patches
        - Oiliness, shine, sebum buildup
        - Scarring, post-acne marks, depressed scars
        - Uneven skin tone, patches of different color
        - Other visible conditions (BUT EXCLUDE normal facial hair)
    
        **EXCLUSIONS (Do NOT report these as conditions):**
        - Normal facial hair, beard, mustache, stubble.
        - Do NOT tag "Facial Hair" or "Stubble" as a skin condition unless it is specifically folliculitis or ingrown hairs.
        
        **For EACH condition you find:**
        1. Create a descriptive name (e.g., "Acne Pustules", "Deep Forehead Wrinkles", "Dark Spots on Cheeks")
        2. Rate confidence 0-100 (how sure are you)
        3. Specify exact location (Forehead, Left Cheek, Right Cheek, Nose, Chin, Under Eyes, Temple, Jaw, etc.)
        4. MANDATORY: A very short, one-sentence description of the problem.
        5. MANDATORY: Draw a bounding box around EVERY visible instance using normalized coordinates (0.0-1.0)
        - x1, y1 = top-left corner
        - x2, y2 = bottom-right corner
        - Example: if acne is on left cheek, draw box around that area
        
        **Grouping Strategy:**
        - Group similar conditions into categories (e.g., "Acne & Blemishes", "Signs of Aging", "Pigmentation Issues", "Texture & Pores")
        - Create new categories as needed based on what you see
        
        Provide output in JSON format. Do NOT return empty arrays for boundingBoxes - every condition MUST have visible boxes.
"""


# ==============================
# BASE64 IMAGE (Upload + Store)
# ==============================
import base64
import tkinter as tk
from tkinter import filedialog
import os

def select_and_convert_image():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp"),
            ("All Files", "*.*")
        ]
    )

    if not file_path:
        print("No file selected.")
        return None

    file_extension = os.path.splitext(file_path)[1].lower().replace(".", "")
    if file_extension == "jpg":
        file_extension = "jpeg"

    with open(file_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:image/{file_extension};base64,{base64_string}"


# 🔥 IMPORTANT: Store the returned value
image_data = select_and_convert_image()

# Check if image was selected
if image_data:
    print("Image converted successfully!")
else:
    print("Image conversion failed.")


# ==============================
# REQUEST BODY
# ==============================

payload = {
    "model": MODEL_NAME,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": analysis_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data
                    }
                }
            ]
        }
    ],
    "temperature": 0.2
}


# ==============================
# API CALL
# ==============================

def analyze_skin():
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        if "choices" not in result:
            print("❌ Unexpected API response format:")
            print(json.dumps(result, indent=2))
            return

        content = result["choices"][0]["message"]["content"]

        print("\n✅ Analysis Result:\n")
        print(content)

    except requests.exceptions.Timeout:
        print("❌ Request timed out")

    except requests.exceptions.RequestException as e:
        print("❌ API Request failed:", str(e))

    except json.JSONDecodeError:
        print("❌ Failed to parse JSON response")


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    analyze_skin()