from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import google.generativeai as genai
import base64
import os
import json

# Configure Gemini API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()

# -----------------------------
# Request Model
# -----------------------------
class AnalyzeRequest(BaseModel):
    images: List[str]


# -----------------------------
# Helper: Convert Base64 to Gemini Part
# -----------------------------
def base64_to_part(base64_string: str):
    try:
        header, encoded = base64_string.split(",", 1)
        mime_type = header.split(";")[0].split(":")[1]

        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": encoded
            }
        }
    except Exception:
        raise ValueError("Invalid base64 image format")


# -----------------------------
# API Route
# -----------------------------
@app.post("/api/analyze-skin")
async def analyze_skin(request: AnalyzeRequest):
    try:
        images = request.images

        if not images or not isinstance(images, list):
            raise HTTPException(
                status_code=400,
                detail="Please provide an array of base64 images in the 'images' field."
            )

        image_parts = [base64_to_part(img) for img in images]

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

        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(
            contents=image_parts + [prompt],
            generation_config={
                "response_mime_type": "application/json"
            }
        )

        result = json.loads(response.text.strip()) if response.text else []

        return result

    except Exception as e:
        print("Error analyzing skin:", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze skin: {str(e)}"
        )