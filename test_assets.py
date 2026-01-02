#!/usr/bin/env python3
"""
Test Kyureki site assets based on folder structure:

root/
  kyureki/
    index.html
    microseason_images/
    data.json
  projects/
    kyureki_scripts/
"""

import os
import json

# Paths
SITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kyureki")
DATA_FILE = os.path.join(SITE_DIR, "data.json")
MICRO_IMG_DIR = os.path.join(SITE_DIR, "microseason_images")

# 1. Check data.json
if not os.path.exists(DATA_FILE):
    print(f"❌ data.json not found at {DATA_FILE}")
else:
    print(f"✅ data.json found at {DATA_FILE}")

    # Load JSON
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # 2. Check normal image
    normal_path = os.path.join(SITE_DIR, data["image"])
    if os.path.exists(normal_path):
        print(f"✅ Normal image found: {normal_path}")
    else:
        print(f"❌ Normal image NOT found: {normal_path}")

    # 3. Check dithered image
    dithered_path = os.path.join(SITE_DIR, data["dithered_image"])
    if os.path.exists(dithered_path):
        print(f"✅ Dithered image found: {dithered_path}")
    else:
        print(f"❌ Dithered image NOT found: {dithered_path}")

    # 4. Print Rokuyo and date for verification
    print(f"ℹ️ Date in JSON: {data['date']}")
    print(f"ℹ️ Rokuyo in JSON: {data['rokuyo']}")
    print(f"ℹ️ Generated at: {data.get('generated_at', 'N/A')}")
