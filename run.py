from bs4 import BeautifulSoup
from pathlib import Path
import csv


def extract_articles(file_path):
    """
    Opens an HTML file and returns all article elements.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")

    return soup.find_all("article", class_="post")


def extract_article_data(article, article_id):
    """
    Extracts metadata from one article.
    """

    title_element = article.find("div", class_="title").find("h2")
    subtitle_element = article.find("div", class_="title").find("p")
    date_element = article.find("time", class_="published")
    author_element = article.find(class_="name")

    title = title_element.text.strip() if title_element else None
    subtitle = subtitle_element.text.strip() if subtitle_element else None
    date = date_element.text.strip() if date_element else None
    author = author_element.text.strip() if author_element else None

    content = article.get_text(separator=" ", strip=True)

    word_count = len(content.split())

    reading_time = max(1, round(word_count / 200))

    return {
        "id": article_id,
        "title": title,
        "subtitle": subtitle,
        "date": date,
        "author": author,
        "word_count": word_count,
        "reading_time_minutes": reading_time
    }


def is_valid_article(article_data):
    """
    Determines whether this is a real article.
    """

    if not article_data["date"]:
        return False

    if not article_data["author"]:
        return False

    if article_data["word_count"] < 100:
        return False

    return True


def export_csv(articles, output_file):
    """
    Creates the content library CSV file.
    """

    fieldnames = [
        "id",
        "title",
        "subtitle",
        "date",
        "author",
        "word_count",
        "reading_time_minutes"
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(articles)


def main():

    print("=" * 50)
    print("Content Museum v0.2")
    print("=" * 50)

    project_folder = Path(__file__).parent

    website_folder = project_folder.parent / "robertsonstuff"

    writing_page = website_folder / "writing.html"

    output_folder = project_folder / "data"

    output_file = output_folder / "content_library.csv"

    print()
    print("Scanning writing.html...")
    print()

    articles = extract_articles(writing_page)

    print(f"Found {len(articles)} possible articles")

    valid_articles = []

    article_number = 1

    for article in articles:

        article_id = f"WRITING-{article_number:03}"

        data = extract_article_data(
            article,
            article_id
        )

        if is_valid_article(data):

            valid_articles.append(data)

            article_number += 1

        else:

            print(
                f"Ignored: {data['title']} "
                "(not a valid article)"
            )

    print()
    print(
        f"Created catalogue with "
        f"{len(valid_articles)} articles"
    )

    output_folder.mkdir(exist_ok=True)

    export_csv(
        valid_articles,
        output_file
    )

    print()
    print("Library created:")
    print(output_file)


if __name__ == "__main__":
    main()