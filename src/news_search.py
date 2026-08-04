import os

import dotenv
import requests

# Load variables from the .env file
dotenv.load_dotenv()

# Read the NewsAPI key
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# NewsAPI endpoint used to search recent articles
NEWS_API_URL = "https://newsapi.org/v2/everything"


def search_news(claim, max_results=5):
    """
    Search for recent news articles related to a claim.
    """

    # Remove unnecessary spaces
    claim = claim.strip()

    # Make sure the claim is not empty
    if not claim:
        raise ValueError("The claim cannot be empty.")

    # Make sure the API key exists
    if not NEWS_API_KEY:
        raise ValueError(
            "NEWS_API_KEY was not found in the .env file."
        )

    # Information sent to NewsAPI
    parameters = {
        "q": claim,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_results,
        "apiKey": NEWS_API_KEY,
    }

    try:
        # Send the request to NewsAPI
        response = requests.get(
            NEWS_API_URL,
            params=parameters,
            timeout=15,
        )

        # Raise an error if the request failed
        response.raise_for_status()

    except requests.Timeout as error:
        raise RuntimeError(
            "The news search request timed out."
        ) from error

    except requests.RequestException as error:
        raise RuntimeError(
            f"News search failed: {error}"
        ) from error

    # Convert the JSON response into Python data
    data = response.json()

    # Get the article list
    articles = data.get("articles", [])

    # Store simplified article results
    results = []

    for article in articles:
        source = article.get("source", {})

        results.append(
            {
                "title": article.get(
                    "title",
                    "Not available",
                ),
                "description": article.get(
                    "description",
                    "Not available",
                ),
                "source": source.get(
                    "name",
                    "Not available",
                ),
                "published_at": article.get(
                    "publishedAt",
                    "Not available",
                ),
                "url": article.get(
                    "url",
                    "Not available",
                ),
            }
        )

    return results


def display_news_results(results):
    """
    Display news-search results in the terminal.
    """

    if not results:
        print("\nNo recent news articles were found.")
        return

    print(f"\nFound {len(results)} recent article(s):")

    for number, article in enumerate(results, start=1):
        print(f"\nArticle {number}")
        print("-" * 40)
        print(f"Title: {article['title']}")
        print(f"Description: {article['description']}")
        print(f"Source: {article['source']}")
        print(f"Published: {article['published_at']}")
        print(f"URL: {article['url']}")


# Run this section only when testing this file directly
if __name__ == "__main__":

    # Ask the user for a claim
    user_claim = input("Enter a claim to search: ")

    try:
        # Search for recent articles
        news_results = search_news(user_claim)

        # Show the results
        display_news_results(news_results)

    except (ValueError, RuntimeError) as error:
        print(f"\nError: {error}")