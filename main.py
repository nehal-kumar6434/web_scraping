from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# -------------------- Logging --------------------
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------- Rating Mapping --------------------
rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

# -------------------- Headers --------------------
headers = {
    "User-Agent": "Mozilla/5.0"
}

# -------------------- Scraping Function --------------------
def scrape_page(page):
    url = f"https://books.toscrape.com/catalogue/page-{page}.html"

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            logging.warning(f"Page {page} not found.")
            return []

        # Fix Encoding
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")

        books = soup.find_all("article", class_="product_pod")

        page_data = []

        for book in books:

            # Title
            title = book.h3.a["title"]

            # Price
            price_text = book.find("p", class_="price_color").get_text(strip=True)

            # Remove all non-numeric characters
            price = float(re.sub(r"[^\d.]", "", price_text))

            # Rating
            rating_text = book.find("p", class_="star-rating")["class"][1]
            rating = rating_map.get(rating_text, 0)

            page_data.append({
                "Title": title,
                "Price": price,
                "Rating": rating,
                "Scraped_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        logging.info(f"Page {page} scraped successfully.")

        return page_data

    except Exception as e:
        logging.error(f"Page {page} Error: {e}")
        return []

# -------------------- Main Program --------------------
all_books = []

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(scrape_page, range(1, 6))

    for result in results:
        all_books.extend(result)

# -------------------- Create DataFrame --------------------
df = pd.DataFrame(all_books)

# Check if data exists
if df.empty:
    print("No data scraped. Please check your internet connection or website.")
    exit()

# -------------------- Save CSV --------------------
df.to_csv(
    "books_advanced.csv",
    index=False,
    encoding="utf-8-sig"
)

# -------------------- Save Excel --------------------
df.to_csv(
    "books_advanced.csv",
    index=False,
    encoding="utf-8-sig"
)
# -------------------- Save SQLite --------------------
try:
    conn = sqlite3.connect("books.db")

    df.to_sql(
        "books",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

except Exception as e:
    print("Database Error:", e)

# -------------------- Output --------------------
print("=" * 50)
print("ADVANCED WEB SCRAPING PROJECT COMPLETED")
print("=" * 50)

print(f"Total Books Scraped : {len(df)}")

print("\nFirst 5 Books:")
print(df.head())

print("\nFiles Created Successfully:")
print("1. books_advanced.csv")
print("2. books_advanced.xlsx")
print("3. books.db")
print("4. scraper.log")
import sqlite3

conn = sqlite3.connect("books.db")
cursor = conn.cursor()

# Table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# Total rows
cursor.execute("SELECT COUNT(*) FROM books;")
print("Total Rows:", cursor.fetchone()[0])

# First 5 rows
cursor.execute("SELECT * FROM books LIMIT 5;")
for row in cursor.fetchall():
    print(row)

conn.close()