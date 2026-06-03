import os
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

# Load configuration variables from .env file
load_dotenv()

app = FastAPI()

# Enable CORS parameters securely for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Comprehensive Mock Database Collection
PRODUCTS = [
    {
        "id": 1,
        "name": "iPhone SE",
        "category": "Electronics",
        "price": 429,
        "description": "Budget-friendly Apple phone."
    },
    {
        "id": 2,
        "name": "Samsung Galaxy S23",
        "category": "Electronics",
        "price": 799,
        "description": "Flagship Android phone."
    },
    {
        "id": 3,
        "name": "Sony WH-1000XM4",
        "category": "Audio",
        "price": 348,
        "description": "Premium wireless headphones."
    },
    {
        "id": 4,
        "name": "Anker Soundcore Life Q30",
        "category": "Audio",
        "price": 80,
        "description": "Excellent budget headphones."
    },
    {
        "id": 5,
        "name": "Dell XPS 13",
        "category": "Computers",
        "price": 999,
        "description": "Sleek ultrabook for professionals."
    },
    {
        "id": 6,
        "name": "Lenovo IdeaPad 3",
        "category": "Computers",
        "price": 350,
        "description": "Reliable laptop for everyday use."
    },
    {
        "id": 7,
        "name": "Google Pixel 8a",
        "category": "Electronics",
        "price": 499,
        "description": "Mid-range Android with stock software and AI camera."
    },
    {
        "id": 8,
        "name": "OnePlus 12R",
        "category": "Electronics",
        "price": 500,
        "description": "Performance phone featuring ultra-fast charging."
    },
    {
        "id": 9,
        "name": "Motorola Moto G Power",
        "category": "Electronics",
        "price": 250,
        "description": "Ultra-budget phone with a massive 3-day battery lifespan."
    },
    {
        "id": 10,
        "name": "Nothing Phone (2)",
        "category": "Electronics",
        "price": 599,
        "description": "Unique clear-back design with customizable LED lights."
    },
    {
        "id": 11,
        "name": "Xiaomi Redmi Note 13",
        "category": "Electronics",
        "price": 220,
        "description": "Affordable entry-level phone with high refresh rates."
    },
    {
        "id": 12,
        "name": "Asus ROG Phone 8",
        "category": "Electronics",
        "price": 1099,
        "description": "High-end gaming phone with cooling and trigger buttons."
    }
]


class PreferenceRequest(BaseModel):
    preference: str


@app.get("/api/products")
def get_products():
    return PRODUCTS


@app.post("/api/recommend")
def recommend_products(request: PreferenceRequest):
    if not os.environ.get("GROQ_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="Server Config Error: GROQ_API_KEY is completely missing."
        )

    sys_prompt = (
        "You are a parsing utility. Analyze the user request against the catalog. "
        "Identify matching product IDs. Output ONLY a valid JSON array of integers. "
        "Example output: [1, 7]"
    )

    user_content = (
        f"Catalog: {json.dumps(PRODUCTS)}\n"
        f"Request: {request.preference}"
    )

    raw_content = ""
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=1,
        )

        raw_content = completion.choices[0].message.content.strip()

        # Extract only bracketed numerical content via regex
        match = re.search(r"\[[\s\d,]*\]", raw_content)
        if match:
            rec_ids = json.loads(match.group(0))
        else:
            # Secondary backup strip logic
            clean_str = raw_content.replace("```json", "").replace("```", "").strip()
            rec_ids = json.loads(clean_str)

        if not isinstance(rec_ids, list):
            rec_ids = []

        return [p for p in PRODUCTS if p["id"] in rec_ids]

    except Exception as e:
        # Catch absolutely every breaking point and send it straight to the screen
        error_details = f"Type: {type(e).__name__} | Message: {str(e)} | AI Output: {raw_content}"
        print("\n" + "!"*50)
        print(f"DIAGNOSTIC EXCEPTION DECTECTED:\n{error_details}")
        print("!"*50 + "\n")
        raise HTTPException(status_code=500, detail=error_details)