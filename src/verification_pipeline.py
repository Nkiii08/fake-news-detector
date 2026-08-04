from src.claim_extractor import extract_claim
from src.evidence_analyzer import analyze_evidence
from src.factcheck_search import search_facts_check
from src.news_search import search_news


def analyze_fact_checks(claim, fact_checks):
    """
    Analyze each published fact-check result.
    """

    analyzed_results = []

    for fact_check in fact_checks:
        # Combine useful fact-check fields into one evidence string
        evidence_text = (
            f"Claim reviewed: {fact_check.get('claim', '')}. "
            f"Rating: {fact_check.get('rating', '')}. "
            f"Review title: {fact_check.get('review_title', '')}."
        )

        # Compare the evidence with the user's claim
        analysis = analyze_evidence(
            claim,
            evidence_text,
        )

        # Store the original result and the analysis together
        analyzed_results.append(
            {
                **fact_check,
                "relationship": analysis["relationship"],
                "confidence": analysis["confidence"],
            }
        )

    return analyzed_results


def analyze_news_articles(claim, news_articles):
    """
    Analyze each retrieved news article.
    """

    analyzed_results = []

    for article in news_articles:
        # Combine the title and description into evidence text
        evidence_text = (
            f"{article.get('title', '')}. "
            f"{article.get('description', '')}"
        ).strip()

        # Skip articles that do not contain useful text
        if not evidence_text:
            continue

        # Compare the article with the user's claim
        analysis = analyze_evidence(
            claim,
            evidence_text,
        )

        # Store the original article and the analysis together
        analyzed_results.append(
            {
                **article,
                "relationship": analysis["relationship"],
                "confidence": analysis["confidence"],
            }
        )

    return analyzed_results


def group_evidence(fact_checks, news_articles):
    """
    Group all evidence by its relationship to the claim.
    """

    grouped_results = {
        "supports": [],
        "contradicts": [],
        "neutral": [],
    }

    all_results = fact_checks + news_articles

    for result in all_results:
        relationship = result["relationship"]

        if relationship == "SUPPORTS":
            grouped_results["supports"].append(result)

        elif relationship == "CONTRADICTS":
            grouped_results["contradicts"].append(result)

        else:
            grouped_results["neutral"].append(result)

    return grouped_results


def verify_news(user_text):
    """
    Run the complete retrieval and evidence-analysis pipeline.
    """

    # Extract a short searchable claim
    claim = extract_claim(user_text)

    # Retrieve published fact checks
    fact_checks = search_facts_check(claim)

    # Retrieve recent news articles
    news_articles = search_news(claim)

    # Analyze each fact-check result
    analyzed_fact_checks = analyze_fact_checks(
        claim,
        fact_checks,
    )

    # Analyze each recent news article
    analyzed_news_articles = analyze_news_articles(
        claim,
        news_articles,
    )

    # Group evidence by relationship
    grouped_evidence = group_evidence(
        analyzed_fact_checks,
        analyzed_news_articles,
    )

    # Return everything together
    return {
        "claim": claim,
        "fact_checks": analyzed_fact_checks,
        "news_articles": analyzed_news_articles,
        "evidence": grouped_evidence,
    }


# Run only when testing this file directly
if __name__ == "__main__":

    # Ask the user for a claim or article
    user_text = input("Enter a claim or article: ")

    try:
        # Run the complete verification pipeline
        result = verify_news(user_text)

        print("\nExtracted claim:")
        print(result["claim"])

        print("\nEvidence summary:")
        print(
            "Supports:",
            len(result["evidence"]["supports"]),
        )
        print(
            "Contradicts:",
            len(result["evidence"]["contradicts"]),
        )
        print(
            "Neutral:",
            len(result["evidence"]["neutral"]),
        )

    except (TypeError, ValueError, RuntimeError) as error:
        print(f"\nError: {error}")