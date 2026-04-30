#!/usr/bin/env python3
"""
Kyureki Generator v1.3
- Downloads today's microseason image from kurashikata.com
- Dithers it for e-ink display
- Fetches today's Rokuyō from the official calendar
- Saves images and data.json into /root/kyureki/
"""

import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from PIL import Image
import io
import json

# -------------------------
# Configuration
# -------------------------

KURASHIKATA_URL = "https://www.kurashikata.com/?post_type=koyomi"
ROKUYO_CALENDAR_URL = "https://rokuyo.org/rokuyo/calendar.php"

# -------------------------
# Paths (AUTHORITATIVE)
# -------------------------

# Absolute path to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Repo root: /root/
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

# Public Kyureki site folder: /root/kyureki
KYUREKI_DIR = os.path.join(REPO_ROOT, "kyureki")

# Assets
MICROSEASON_IMAGES_DIR = os.path.join(KYUREKI_DIR, "microseason_images")
DATA_FILE = os.path.join(KYUREKI_DIR, "data.json")

IMAGE_NORMAL = os.path.join(
    MICROSEASON_IMAGES_DIR, "current_microseason.jpg")
IMAGE_DITHERED = os.path.join(
    MICROSEASON_IMAGES_DIR, "current_microseason_dithered.jpg")

# Debug sanity check (intentional)
print("Script dir:", SCRIPT_DIR)
print("Repo root:", REPO_ROOT)
print("Kyureki output dir:", KYUREKI_DIR)

# Ensure output folders exist
os.makedirs(MICROSEASON_IMAGES_DIR, exist_ok=True)

# -------------------------
# Rokuyo mapping
# -------------------------

ROKUYO_MAP = {
    "se": "Sensho",
    "to": "Tomobiki",
    "sm": "Sakimake",
    "bu": "Butsumetsu",
    "ta": "Taian",
    "sk": "Shakku",
}

# -------------------------
# Utility functions
# -------------------------

def dither_image(image_data):
    """Dither image to 7-color e-ink palette"""
    img = Image.open(io.BytesIO(image_data)).convert("RGB")

    palette = [
        0, 0, 0,        # Black
        255, 255, 255,  # White
        255, 0, 0,      # Red
        255, 255, 0,    # Yellow
        0, 0, 255,      # Blue
        0, 255, 0,      # Green
        255, 140, 0     # Orange
    ]
    palette += [0] * (768 - len(palette))

    palette_img = Image.new("P", (1, 1))
    palette_img.putpalette(palette)

    return img.quantize(
        palette=palette_img,
        dither=Image.Dither.FLOYDSTEINBERG
    ).convert("RGB")

# -------------------------
# Microseason image scraping
# -------------------------

def scrape_microseason_image():
    resp = requests.get(KURASHIKATA_URL, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")
    img_tag = soup.find(
        "img",
        src=lambda x: x and "/wp-content/uploads/" in x and x.endswith(".jpg")
    )

    if not img_tag:
        raise RuntimeError("Microseason image not found")

    img_url = img_tag["src"]
    img_resp = requests.get(img_url, timeout=30)
    img_resp.raise_for_status()

    # Save normal image
    with open(IMAGE_NORMAL, "wb") as f:
        f.write(img_resp.content)

    # Save dithered image
    dithered = dither_image(img_resp.content)
    dithered.save(IMAGE_DITHERED, "JPEG", quality=95)

# -------------------------
# Rokuyo scraping
# -------------------------

def get_today_rokuyo():
    resp = requests.get(ROKUYO_CALENDAR_URL, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")
    today_day = datetime.now().day

    for td in soup.find_all("td"):
        parts = td.get_text("\n").strip().split("\n")
        if len(parts) == 2 and parts[0].isdigit():
            if int(parts[0]) == today_day:
                return ROKUYO_MAP.get(parts[1].lower(), "Unknown")

    return "Unknown"

# -------------------------
# Generate data.json
# -------------------------

def generate_site_data():
    data = {
        "date": datetime.now().strftime("%A, %B %d, %Y"),
        "rokuyo": get_today_rokuyo(),
        "image": "microseason_images/current_microseason.jpg",
        "dithered_image": "microseason_images/current_microseason_dithered.jpg",
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# -------------------------
# Main
# -------------------------

if __name__ == "__main__":
    print("Starting Kyureki Generator...")
    scrape_microseason_image()
    generate_site_data()
    print(f"Kyureki artifacts generated in {KYUREKI_DIR}")
