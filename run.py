
from bs4 import BeautifulSoup
from pathlib import Path
import sys


def extract_articles(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")

    articles = soup.find_all("article", class_="post")

    return articles


def extract_article_data(article):
    title = article.find("div", class_="title").find("h2").text.strip()

    subtitle = article.find("div", class_="title").find("p").text.strip()

    date = article.find("time", class_="published").text.strip()

    author = article.find(class_="name").text.strip()

    content = article.get_text(separator=" ", strip=True)

    word_count = len(content.split())

    reading_time = round(word_count / 200)

    return {
        "title": title,
        "subtitle": subtitle,
        "date": date,
        "author": author,
        "word_count": word_count,
        "reading_time": reading_time
    }


def main():

    print("=" * 40)
    print("Content Museum v0.1")
    print("=" * 40)

    website_path = Path("../robertsonstuff")

    writing_page = website_path / "writing.html"

    print("\nScanning writing.html...\n")

    articles = extract_articles(writing_page)

    print(f"Found {len(articles)} articles\n")

    for index, article in enumerate(articles, start=1):

        data = extract_article_data(article)

        print(f"ARTICLE {index}")
        print("-" * 40)

        print(f"Title: {data['title']}")
        print(f"Published: {data['date']}")
        print(f"Words: {data['word_count']}")
        print(f"Reading time: {data['reading_time']} minutes")

        print()


if __name__ == "__main__":
    main()
