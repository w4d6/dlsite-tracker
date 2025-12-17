#!/usr/bin/env python3
"""DLsite work information tracker - Fetches data and writes to Google Sheets."""

import argparse
import json
import os
from datetime import datetime
from typing import Optional
import requests
import gspread
from google.oauth2.service_account import Credentials

# Target product IDs
PRODUCT_IDS = [
    "RJ01486587",  # Announce page
    "RJ01470011",  # Work page
]

# Google Sheets configuration
SPREADSHEET_ID = "1dxg6vN351JC6Zg2Set2ipq7Dp7H5lzbJRgdmyG7X30g"
SHEET_NAME = "シート1"  # Default sheet name

# DLsite API endpoint
DLSITE_API_URL = "https://www.dlsite.com/maniax/product/info/ajax"


def fetch_dlsite_info(product_id: str) -> Optional[dict]:
    """Fetch product information from DLsite API."""
    try:
        response = requests.get(
            DLSITE_API_URL,
            params={"product_id": product_id},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get(product_id)
    except Exception as e:
        print(f"Error fetching {product_id}: {e}")
        return None


def get_product_url(product_id: str, is_announce: bool) -> str:
    """Generate the DLsite URL for a product."""
    if is_announce:
        return f"https://www.dlsite.com/maniax/announce/=/product_id/{product_id}.html"
    return f"https://www.dlsite.com/maniax/work/=/product_id/{product_id}.html"


def get_google_sheets_client():
    """Initialize Google Sheets client with service account credentials."""
    # Get credentials from environment variable (JSON string)
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not set")

    creds_dict = json.loads(creds_json)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(credentials)


def write_to_sheet(records: list[dict], mode: str = "all"):
    """Write records to Google Sheets.

    Args:
        records: List of record dictionaries
        mode: "wishlist" for favorites only, "sales" for sales only, "all" for both
    """
    client = get_google_sheets_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    try:
        worksheet = spreadsheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.sheet1

    # Check if header exists
    existing_data = worksheet.get_all_values()
    if not existing_data:
        # Add header row
        header = ["実行日付", "タイトル", "URL", "お気に入り数", "販売数", "取得種別"]
        worksheet.append_row(header)

    # Append each record
    for record in records:
        # Determine what to write based on mode
        if mode == "wishlist":
            wishlist_val = record["wishlist_count"]
            dl_val = ""
            source = "お気に入り"
        elif mode == "sales":
            wishlist_val = ""
            dl_val = record["dl_count"]
            source = "販売数"
        else:
            wishlist_val = record["wishlist_count"]
            dl_val = record["dl_count"]
            source = "全取得"

        row = [
            record["date"],
            record["title"],
            record["url"],
            wishlist_val,
            dl_val,
            source,
        ]
        worksheet.append_row(row)
        print(f"Added: {record['title']} ({source})")


def main():
    """Main function to fetch DLsite data and write to Google Sheets."""
    parser = argparse.ArgumentParser(description="DLsite tracker")
    parser.add_argument(
        "--mode",
        choices=["wishlist", "sales", "all"],
        default="all",
        help="Data to fetch: wishlist (favorites), sales (download count), or all",
    )
    args = parser.parse_args()

    mode = args.mode
    mode_names = {"wishlist": "お気に入り数", "sales": "販売数", "all": "全データ"}
    print(f"Mode: {mode_names[mode]}")

    today = datetime.now().strftime("%Y-%m-%d")
    records = []

    for product_id in PRODUCT_IDS:
        print(f"Fetching {product_id}...")
        info = fetch_dlsite_info(product_id)

        if info:
            is_announce = info.get("is_ana", False)
            dl_count = info.get("dl_count")

            record = {
                "date": today,
                "title": info.get("work_name", "Unknown"),
                "url": get_product_url(product_id, is_announce),
                "wishlist_count": info.get("wishlist_count", 0),
                "dl_count": dl_count if dl_count is not None else "N/A",
            }
            records.append(record)
            print(f"  Title: {record['title']}")
            if mode in ["wishlist", "all"]:
                print(f"  Wishlist: {record['wishlist_count']}")
            if mode in ["sales", "all"]:
                print(f"  DL Count: {record['dl_count']}")
        else:
            print(f"  Failed to fetch info for {product_id}")

    if records:
        print("\nWriting to Google Sheets...")
        write_to_sheet(records, mode)
        print("Done!")
    else:
        print("No records to write.")


if __name__ == "__main__":
    main()
