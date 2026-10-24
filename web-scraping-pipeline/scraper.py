
import csv
import json
import time
from collections import Counter
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://quotes.toscrape.com/"
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)


def create_session():
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    session = requests.Session()
    session.headers.update({
        "User-Agent": "StudentWebScrapingProject/1.0"
    })
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def scrape_quotes():
    session = create_session()
    response = session.get(URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    records = []

    for item in soup.select(".quote"):
        quote = item.select_one(".text")
        author = item.select_one(".author")
        tags = item.select(".tags .tag")

        if quote and author:
            records.append({
                "quote": quote.get_text(strip=True),
                "author": author.get_text(strip=True),
                "tags": ", ".join(
                    tag.get_text(strip=True) for tag in tags
                ),
            })

    time.sleep(1)
    return records


def save_data(records):
    with open(OUTPUT / "quotes.json", "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)

    with open(
        OUTPUT / "quotes.csv", "w",
        newline="", encoding="utf-8"
    ) as file:
        fields = ["quote", "author", "tags"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def generate_report(records):
    authors = Counter(record["author"] for record in records)

    report = {
        "total_records": len(records),
        "unique_authors": len(authors),
        "top_authors": authors.most_common(5),
    }

    with open(OUTPUT / "report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\n--- Scraping Report ---")
    print("Total records:", report["total_records"])
    print("Unique authors:", report["unique_authors"])
    print("Top authors:", report["top_authors"])


def main():
    try:
        records = scrape_quotes()

        if not records:
            print("No records found. Check the webpage structure.")
            return

        save_data(records)
        generate_report(records)
        print("Files saved in the output folder.")

    except requests.RequestException as error:
        print("Network or webpage error:", error)
    except (OSError, ValueError) as error:
        print("File or data error:", error)


if __name__ == "__main__":
    main()

