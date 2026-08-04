from src.claim_extractor import extract_claim
from src.factcheck_search import search_facts_check
from src.news_search import search_news


def verify_news(user_text):
    # Extract a claim and retrieve related fact checks and recent news.
     # Extract a short searchable claim
    claim = extract_claim(user_text)

    # Search for published fact checks
    fact_checks = search_facts_check(claim)

    # Search for recent news articles
    news_articles = search_news(claim)

    # Return all results together
    return {
        "claim": claim,
        "fact_checks": fact_checks,
        "news_articles": news_articles,
    }

# Run this section only when testing the file directly
if __name__ == "__main__":

    # Ask the user to enter a claim or article
    user_text = input("Enter a claim or article: ")

    try:
        # Run the verification pipeline
        result = verify_news(user_text)

        # Show the extracted claim
        print("\nExtracted claim:")
        print(result["claim"])

        # Show the number of fact-check results
        print("\nFact-check results:")
        print(len(result["fact_checks"]))

        # Show the number of recent news results
        print("\nRecent news results:")
        print(len(result["news_articles"]))

    except (TypeError, ValueError, RuntimeError) as error:
        print(f"\nError: {error}")