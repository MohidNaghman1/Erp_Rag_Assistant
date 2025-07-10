import os
import json
import re
from dotenv import load_dotenv
from scrapper import EnhancedErpScraper

if __name__ == "__main__":
    load_dotenv()
    ROLL_NO = os.getenv("ERP_ROLL_NO")
    PASSWORD = os.getenv("ERP_PASSWORD")
    DATA_FOLDER = "data"

    if not ROLL_NO or not PASSWORD:
        print("❌ Error: Set ERP_ROLL_NO and ERP_PASSWORD in your .env file.")
        exit()

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"Created directory: '{DATA_FOLDER}'")

    try:
        with EnhancedErpScraper(ROLL_NO, PASSWORD) as scraper:
            all_data = scraper.scrape_all_data()

        if "error" in all_data:
            print("\nScraping process failed. Please check the error messages above.")
            exit()

        # ✅ Save by Roll Number instead of student name
        safe_roll_no = re.sub(r'[\\/*?:"<>|]', "", ROLL_NO).replace(' ', '_')
        file_path = os.path.join(DATA_FOLDER, f"{safe_roll_no}.json")

        print(f"\n--- Saving All Data ---")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4)

        print(f"\n✅✅✅ Success! All data saved to: {file_path}")

    except Exception as e:
        print(f"\n❌ A fatal error occurred in the main script: {e}")
