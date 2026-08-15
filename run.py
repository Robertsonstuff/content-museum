from bs4 import BeautifulSoup
from pathlib import Path
import csv
import json


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

    title_container = article.find("div", class_="title")

    title_element = (
        title_container.find("h2")
        if title_container
        else None
    )

    subtitle_element = (
        title_container.find("p")
        if title_container
        else None
    )

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


def load_exhibitions(file_path):
    """
    Opens exhibitions.json and returns the museum structure.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_exhibitions(museum, articles):
    """
    Checks that every article referenced by an exhibition
    actually exists in the content library.
    """

    article_lookup = {
        article["id"]: article
        for article in articles
    }

    print()
    print("Checking exhibition references...")
    print()

    all_valid = True
    assigned_ids = set()

    for exhibition in museum["exhibitions"]:

        print(exhibition["title"])
        print("-" * 40)

        artifact_ids = exhibition.get("artifact_ids", [])

        for artifact_id in artifact_ids:

            if artifact_id in article_lookup:

                article = article_lookup[artifact_id]

                print(
                    f"  ✓ {artifact_id} — "
                    f"{article['title']}"
                )

                assigned_ids.add(artifact_id)

            else:

                print(
                    f"  ✗ {artifact_id} — "
                    "ARTICLE NOT FOUND"
                )

                all_valid = False

        print()

    return all_valid, assigned_ids


def report_unassigned_articles(articles, assigned_ids):
    """
    Identifies valid articles that have not yet been
    assigned to an exhibition.
    """

    unassigned = [
        article
        for article in articles
        if article["id"] not in assigned_ids
    ]

    print("Checking for unassigned articles...")
    print()

    if not unassigned:

        print("  ✓ All articles are assigned to an exhibition.")

    else:

        print(
            f"  Found {len(unassigned)} "
            "unassigned article(s):"
        )

        for article in unassigned:

            print(
                f"  • {article['id']} — "
                f"{article['title']}"
            )

    print()

    return unassigned


def print_museum_summary(museum, articles):
    """
    Prints a high-level summary of the museum.
    """

    print("=" * 50)
    print("MUSEUM SUMMARY")
    print("=" * 50)

    print()
    print(f"Museum: {museum['museum']['name']}")
    print(f"Tagline: {museum['museum']['tagline']}")
    print()

    print(
        f"Exhibitions: "
        f"{len(museum['exhibitions'])}"
    )

    print(
        f"Articles: "
        f"{len(articles)}"
    )

    print()

    for exhibition in museum["exhibitions"]:

        artifact_count = len(
            exhibition.get("artifact_ids", [])
        )

        anchor = exhibition.get("anchor_artifact")

        print(
            f"• {exhibition['title']}: "
            f"{artifact_count} artifacts"
        )

        if anchor:

            print(
                f"  Anchor: {anchor}"
            )

    print()


def main():

    print("=" * 50)
    print("Content Museum v0.3")
    print("=" * 50)

    project_folder = Path(__file__).parent

    website_folder = (
        project_folder.parent / "robertsonstuff"
    )

    writing_page = (
        website_folder / "writing.html"
    )

    data_folder = (
        project_folder / "data"
    )

    output_file = (
        data_folder / "content_library.csv"
    )

    exhibitions_file = (
        data_folder / "exhibitions.json"
    )

    # ----------------------------------------
    # Load museum structure
    # ----------------------------------------

    print()
    print("Loading museum structure...")

    museum = load_exhibitions(
        exhibitions_file
    )

    print(
        f"Found "
        f"{len(museum['exhibitions'])} exhibitions"
    )

    # ----------------------------------------
    # Extract articles
    # ----------------------------------------

    print()
    print("Scanning writing.html...")
    print()

    articles = extract_articles(
        writing_page
    )

    print(
        f"Found {len(articles)} "
        "possible articles"
    )

    # ----------------------------------------
    # Validate articles
    # ----------------------------------------

    valid_articles = []

    article_number = 1

    for article in articles:

        # Temporary ID used only while
        # determining whether this is a
        # genuine article.

        temporary_id = (
            f"WRITING-{article_number:03}"
        )

        data = extract_article_data(
            article,
            temporary_id
        )

        if is_valid_article(data):

            # IMPORTANT:
            # Only increment the permanent
            # article number when the article
            # passes validation.

            article_number += 1

            data["id"] = (
                f"WRITING-"
                f"{len(valid_articles) + 1:03}"
            )

            valid_articles.append(data)

        else:

            print(
                f"Ignored: {data['title']} "
                "(not a valid article)"
            )

    # ----------------------------------------
    # Export content library
    # ----------------------------------------

    print()
    print(
        f"Created catalogue with "
        f"{len(valid_articles)} articles"
    )

    data_folder.mkdir(
        exist_ok=True
    )

    export_csv(
        valid_articles,
        output_file
    )

    print()
    print("Library created:")
    print(output_file)

    # ----------------------------------------
    # Validate exhibitions
    # ----------------------------------------

    all_valid, assigned_ids = (
        validate_exhibitions(
            museum,
            valid_articles
        )
    )

    # ----------------------------------------
    # Find unassigned articles
    # ----------------------------------------

    unassigned = (
        report_unassigned_articles(
            valid_articles,
            assigned_ids
        )
    )

    # ----------------------------------------
    # Museum summary
    # ----------------------------------------

    print_museum_summary(
        museum,
        valid_articles
    )

    # ----------------------------------------
    # Final result
    # ----------------------------------------

    print("=" * 50)

    if all_valid:

        print(
            "✓ All exhibition references "
            "are valid."
        )

    else:

        print(
            "✗ Some exhibition references "
            "could not be found."
        )

    if unassigned:

        print(
            "⚠ Some articles are not yet "
            "assigned to an exhibition."
        )

    else:

        print(
            "✓ All articles are assigned."
        )

    print("=" * 50)


if __name__ == "__main__":
    main()