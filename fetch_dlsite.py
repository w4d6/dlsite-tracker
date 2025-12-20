#!/usr/bin/env python3
"""DLsite data fetcher - writes to Google Sheets"""

import argparse
import json
import os
from datetime import datetime
import requests
import gspread
from google.oauth2.service_account import Credentials

PRODUCT_IDS = ["RJ01486587", "RJ01470011"]
API_URL = "https://www.dlsite.com/maniax/product/info/ajax"

# Google Sheets configuration
SPREADSHEET_ID = "1dxg6vN351JC6Zg2Set2ipq7Dp7H5lzbJRgdmyG7X30g"
SHEET_NAME = "シート1"


def get_google_sheets_client():
    """Initialize Google Sheets client with service account credentials."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_json:
        # Use environment variable (for GitHub Actions)
        creds_dict = json.loads(creds_json)
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    else:
        # Use Application Default Credentials (for local development)
        import google.auth
        credentials, _ = google.auth.default(scopes=scopes)

    return gspread.authorize(credentials)


def write_to_sheet(records: list[dict], mode: str):
    """Write records to Google Sheets."""
    client = get_google_sheets_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    try:
        worksheet = spreadsheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.sheet1

    # Check if header exists
    existing_data = worksheet.get_all_values()
    if not existing_data:
        header = ["実行日付", "タイトル", "URL", "お気に入り数", "販売数", "取得種別"]
        worksheet.append_row(header)

    # Append each record
    for record in records:
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
    parser = argparse.ArgumentParser(description="DLsite data fetcher")
    parser.add_argument(
        "--mode",
        choices=["wishlist", "sales", "all"],
        default="all",
        help="Data to fetch: wishlist, sales, or all",
    )
    args = parser.parse_args()
    mode = args.mode

    mode_names = {"wishlist": "お気に入り数", "sales": "販売数", "all": "全データ"}
    print(f"Mode: {mode_names[mode]}")

    today = datetime.now().strftime("%Y-%m-%d")

    # Fetch all products in one request
    params = [("product_id[]", pid) for pid in PRODUCT_IDS]
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    records = []
    for product_id in PRODUCT_IDS:
        info = data.get(product_id)
        if info:
            is_announce = info.get("is_ana", False)
            url = f"https://www.dlsite.com/maniax/{'announce' if is_announce else 'work'}/=/product_id/{product_id}.html"
            dl_count = info.get("dl_count")

            # Pre-sale (announce) items don't have sales data yet
            if is_announce:
                dl_count_display = "販売開始前"
            elif dl_count is not None:
                dl_count_display = dl_count
            else:
                dl_count_display = "N/A"

            record = {
                "date": today,
                "title": info.get("work_name", "Unknown"),
                "url": url,
                "wishlist_count": info.get("wishlist_count", 0),
                "dl_count": dl_count_display,
            }
            records.append(record)
            print(f"Fetched: {record['title']}")
        else:
            print(f"Failed to fetch: {product_id}")

    if records:
        print("\nWriting to Google Sheets...")
        write_to_sheet(records, mode)
        print("Done!")
    else:
        print("No records to write.")


if __name__ == "__main__":
    main()
