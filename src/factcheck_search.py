import os

import requests
from dotenv import load_dotenv

#load environment variables from .env file
load_dotenv()

# Read the Google API key
api_key = os.getenv("GOOGLE_FACTCHECK_API_KEY")

# Google fact check API endpoint
FACT_CHECK_URL = (
    "https://factchecktools.googleapis.com/"
    "v1alpha1/claims:search"
)

def search_facts_check(claim, max_results=5):

    #Search for published fact checks related to a claim.
    claim = claim.strip()

    if not claim:
        raise ValueError("Claim cannot be empty.")

    # Make sure the API key exists
    if not api_key:
        raise ValueError("GOOGLE_FACTCHECK_API_KEY was not found in the .env file.") 

    # Information sent to the google API
    parameters = {
        "query": claim,
        "key": api_key,
        "pageSize": max_results,
       
    }

    try:
        # Send the request to google
        response = requests.get(
            FACT_CHECK_URL,
            params=parameters,
            timeout=15,
        )

        # Raise an error if the request fails
        response.raise_for_status()

    except requests.Timeout as error:

        raise RuntimeError(
            "The fact-check request timed out."
        ) from error

    except requests.RequestException as error:

        raise RuntimeError(
            f"Fact-check request failed: {error}"
        ) from error

    # Convert the JSON response to a Python data
    data = response.json()

    # Get the claims list, or use an empty list
    claims = data.get("claims", [])

    # Store simplified results
    results = []

    for claim_result in claims:
        reviews = claim_result.get("claimReview", [])

        for review in reviews:
            publisher = review.get("publisher", {})

            results.append({
                "claim": claim_result.get(
                    "text",
                    "Not available",
                ),
                "claimant": claim_result.get(
                    "claimant",
                    "Not available",
                ),
                "rating": review.get(
                    "textualRating",
                    "Not available",
                ),
                "publisher": publisher.get(
                    "name",
                    "Not available",
                ),
                "review_title": review.get(
                    "title",
                    "Not available",
                ),
                "review_date": review.get(
                    "reviewDate",
                    "Not available",
                ),
                "url": review.get(
                    "url",
                    "Not available",
                ),
            })

    return results
def display_fact_check_results(results):
    if not results:
        print("No fact-check results found.")
        return

    for i, result in enumerate(results, start=1):
        print(f"\nResult {i}:")
        print(f"Claim: {result['claim']}")
        print(f"Claimant: {result['claimant']}")
        print(f"Rating: {result['rating']}")
        print(f"Publisher: {result['publisher']}")
        print(f"Review Title: {result['review_title']}")
        print(f"Review Date: {result['review_date']}")
        print(f"URL: {result['url']}")

# Run this section only when testing this file directly
if __name__ == "__main__":

    # Ask the user for a claim
    user_claim = input("Enter a claim to fact-check: ")

    try:
        # Search for fact checks
        fact_check_results = search_facts_check(user_claim)

        # Show the results
        display_fact_check_results(fact_check_results)

    except (ValueError, RuntimeError) as error:
        print(f"\nError: {error}")

