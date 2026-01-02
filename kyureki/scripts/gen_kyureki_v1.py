#!/usr/bin/env python3
"""
Kyureki Generator v2
- Downloads today's microseason image from kurashikata.com
- Dithers it for e-ink display
- Fetches today's Rokuyō from the official calendar
- Saves everything in site_output/ folder
"""

import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image
import io

# -------------------------
# Configuration
# -------------------------

KURASHIKATA_URL = "https://www.kurashikata.com/?post_type=koyomi"
ROKUYO_CALENDAR_URL = "https://rokuyo.org/rokuyo/calendar.php"

# Output paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "site_output")
IMAGE_DIR = os.path.join(OUTPUT_DIR, "microseason_images")
DATA_FILE = os.path.join(OUTPUT_DIR, "data.json")

CURRENT_IMAGE = "current_microseason.jpg"
CURRENT_DITHERED_IMAGE = "current_microseason_dithered.jpg"

# Rokuyo mapping
ROKUYO_MAP = {
    "se": "Sensho",
    "to": "Tomobiki",
    "sm": "Sakimake",
    "bu": "Butsumetsu",
    "ta": "Taian",
    "sk": "Shakku",
}

# Ensure output folders exist
os.makedirs(IMAGE_DIR, exist_ok=True)

# -------------------------
# Utility functions
# -------------------------

def dither_image(image_data):
    """Dither image to 7-color e-ink palette"""
    img = Image.open(io.BytesIO(image_data))
    if img.mode != "RGB":
        img = img.convert("RGB")

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

    dithered = img.quantize(palette=palette_img, dither=Image.Dither.FLOYDSTEINBERG)
    return dithered.convert("RGB")

# -------------------------
# Microseason image scraping
# -------------------------

def scrape_microseason_image():
    """Download and save the current microseason image"""
    try:
        print(f"Fetching page: {KURASHIKATA_URL}")
        resp = requests.get(KURASHIKATA_URL, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, "html.parser")
        img_tag = soup.find("img", src=lambda x: x and "/wp-content/uploads/" in x and x.endswith(".jpg"))

        if not img_tag:
            print("Could not find microseason image")
            return False

        img_url = img_tag["src"]
        print(f"Found image: {img_url}")

        img_resp = requests.get(img_url, timeout=30)
        img_resp.raise_for_status()

        # Save current images
        current_path = os.path.join(IMAGE_DIR, CURRENT_IMAGE)
        dithered_path = os.path.join(IMAGE_DIR, CURRENT_DITHERED_IMAGE)

        with open(current_path, "wb") as f:
            f.write(img_resp.content)
        print(f"Saved current image: {current_path}")

        dithered_img = dither_image(img_resp.content)
        dithered_img.save(dithered_path, "JPEG", quality=95)
        print(f"Saved dithered image: {dithered_path}")

        return True

    except Exception as e:
        print(f"Error scraping microseason image: {e}")
        return False

# -------------------------
# Rokuyo scraping from calendar
# -------------------------

def get_today_rokuyo():
    """Scrape the Rokuyō calendar and return today's day"""
    try:
        resp = requests.get(ROKUYO_CALENDAR_URL, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")

        today_day = datetime.today().day  # e.g., 1, 2, ...
        # The calendar page uses <td> or <span> for each day, look for matching day number
        # Each <td> has format: "1\nta" or similar

        for td in soup.find_all("td"):
            if td.text.strip() == "":
                continue
            text = td.get_text(separator="\n").strip().split("\n")
            if len(text) < 2:
                continue
            day_num = text[0].strip()
            code = text[1].strip()
            if str(today_day) == day_num:
                return ROKUYO_MAP.get(code.lower(), "Unknown")

        return "Unknown"

    except Exception as e:
        print(f"Error scraping Rokuyo calendar: {e}")
        return "Unknown"

# -------------------------
# Generate site data
# -------------------------

def generate_site_data():
    today_str = datetime.today().strftime("%A, %B %d, %Y")
    rokuyo_day = get_today_rokuyo()

    data = {
        "date": today_str,
        "rokuyo": rokuyo_day,
        "image": os.path.join("microseason_images", CURRENT_IMAGE),
        "dithered_image": os.path.join("microseason_images", CURRENT_DITHERED_IMAGE)
    }

    import json
    with open(os.path.join(OUTPUT_DIR, "data.json"), "w") as f:
        json.dump(data, f, indent=2)
    print(f"Site data saved to {DATA_FILE}")

# -------------------------
# Main
# -------------------------

if __name__ == "__main__":
    print("Starting Kyureki Generator...")

    scrape_microseason_image()
    generate_site_data()

    print("\nKyureki generation complete. Copy site_output/ to your GitHub Pages repo.")
