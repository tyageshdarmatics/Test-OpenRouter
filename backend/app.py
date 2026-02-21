from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# Load API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


# -----------------------------
# Request Model
# -----------------------------
class AnalyzeRequest(BaseModel):
    images: List[str]


# -----------------------------
# Convert Base64 for Gemini
# -----------------------------
def base64_to_gemini_part(base64_string: str):
    header, encoded = base64_string.split(",", 1)
    mime_type = header.split(";")[0].split(":")[1]

    return {
        "inline_data": {
            "mime_type": mime_type,
            "data": encoded
        }
    }


# -----------------------------
# Convert Base64 for OpenAI-style APIs
# -----------------------------
def base64_to_openai_image(base64_string: str):
    return {
        "type": "input_image",
        "image_base64": base64_string.split(",")[1]
    }


# -----------------------------
# Gemini Call
# -----------------------------
def call_gemini(images, prompt):
    try:
        print("Trying Gemini...")
        image_parts = [base64_to_gemini_part(img) for img in images]

        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(
            contents=image_parts + [prompt],
            generation_config={"response_mime_type": "application/json"}
        )

        return json.loads(response.text.strip())
    except Exception as e:
        print("Gemini failed:", e)
        return None


# -----------------------------
# OpenRouter Call
# -----------------------------
def call_openrouter(images, prompt):
    try:
        print("Trying OpenRouter...")

        url = "https://openrouter.ai/api/v1/chat/completions"

        content = [{"type": "text", "text": prompt}]
        content += [base64_to_openai_image(img) for img in images]

        payload = {
            "model": "qwen/qwen3-vl-30b-a3b-thinking",
            # "model": "nvidia/nemotron-nano-12b-v2-vl:free",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)

        data = response.json()
        text = data["choices"][0]["message"]["content"]

        return json.loads(text)
    except Exception as e:
        print("OpenRouter failed:", e)
        return None


# -----------------------------
# Groq Call
# -----------------------------
def call_groq(images, prompt):
    try:
        print("Trying Groq...")

        url = "https://api.groq.com/openai/v1/chat/completions"

        content = [{"type": "text", "text": prompt}]
        content += [base64_to_openai_image(img) for img in images]

        payload = {
            "model": "llama-3.2-11b-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)

        data = response.json()
        text = data["choices"][0]["message"]["content"]

        return json.loads(text)
    except Exception as e:
        print("Groq failed:", e)
        return None


# -----------------------------
# API Route With Failover
# -----------------------------
@app.post("/api/analyze-skin")
async def analyze_skin(request: AnalyzeRequest):
    try:
        images = request.images

        if not images or not isinstance(images, list):
            raise HTTPException(
                status_code=400,
                detail="Provide array of base64 images in 'images'"
            )

        prompt = """
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

        # 1️⃣ Gemini
        result = call_gemini(images, prompt)
        if result:
            print("Success from Gemini")
            return result

        # 2️⃣ OpenRouter
        result = call_openrouter(images, prompt)
        if result:
            print("Success from OpenRouter")
            return result

        # # 3️⃣ Groq
        # result = call_groq(images, prompt)
        # if result:
        #     print("Success from Groq")
        #     return result

        # 4️⃣ If All Fail
        raise HTTPException(
            status_code=500,
            detail="All AI providers failed"
        )

    except Exception as e:
        print("Final Error:", e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )