import csv
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com/"
OUTPUT_FILE = Path(__file__).parent / "books.csv"


def fetch_page(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response.text


def parse_books(html):
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for book in soup.find_all("article", class_="product_pod"):
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text
        books.append({"title": title, "price": price})
    return books


def save_to_csv(books, filename):
    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "price"])
        writer.writeheader()
        writer.writerows(books)


def main():
    try:
        html = fetch_page(URL)
    except requests.exceptions.RequestException as error:
        print(f"Error: Could not retrieve the page. {error}")
        return

    books = parse_books(html)
    if not books:
        print("No books found. The page layout may have changed.")
        return

    save_to_csv(books, OUTPUT_FILE)
    print(f"Scraped {len(books)} books and saved them to {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()