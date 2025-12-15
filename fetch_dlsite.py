#!/usr/bin/env python3
"""DLsite data fetcher - saves CSV"""

import csv
import os
from datetime import datetime
import requests

PRODUCT_IDS = ["RJ01486587", "RJ01470011"]
API_URL = "https://www.dlsite.com/maniax/product/info/ajax"

def main():
    today = datetime.now().strftime("%Y-%m-%d")

    # Fetch all products in one request
    params = [("product_id[]", pid) for pid in PRODUCT_IDS]
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Write latest.csv
    with open("data/latest.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["実行日付", "タイトル", "URL", "お気に入り数", "販売数", "取得元"])

        for product_id in PRODUCT_IDS:
            info = data.get(product_id)
            if info:
                is_announce = info.get("is_ana", False)
                url = f"https://www.dlsite.com/maniax/{'announce' if is_announce else 'work'}/=/product_id/{product_id}.html"
                dl_count = info.get("dl_count")
                writer.writerow([
                    today,
                    info.get("work_name", "Unknown"),
                    url,
                    info.get("wishlist_count", 0),
                    dl_count if dl_count is not None else "N/A",
                    "actions"
                ])
                print(f"Fetched: {info.get('work_name')}")

    print(f"Saved to data/latest.csv")

if __name__ == "__main__":
    main()
