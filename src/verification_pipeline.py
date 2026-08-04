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

def determine_verdict(grouped_evidence, minimum_confidence = 0.70):
    # Determine the overall verdict based on the grouped evidence and a minimum confidence threshold.

    # Keep only evidence with reasonable model confidence
    strong_support = [
        item
        for item in grouped_evidence["supports"]
        if item["confidence"] >= minimum_confidence
    ]

    strong_contradict = [
        item
        for item in grouped_evidence["contradicts"]
        if item["confidence"] >= minimum_confidence
    ]

    support_count = len(strong_support)
    contradicts_count = len(strong_contradict)

    # Conflicting evidence should not produce a definite verdict
    if support_count > 0 and contradicts_count > 0:
        return {
            "verdict": "INCONCLUSIVE",
            "reason": (
                "There is strong evidence both supporting and "
                "contradicting the claim."
            ),
            "support_count": support_count,
            "contradicts_count": contradicts_count,
        }

    # Require at least two strong supporting results to produce a verdict
    if support_count >= 2:
        return{
            "verdict": "SUPPORTED",
            "reason": (
                "There is strong evidence supporting the claim."
            ),
            "support_count": support_count,
            "contradicts_count": contradicts_count,
        }

    # Use unverified evidence when evidence is missing or weak
    return{
        "verdict": "UNVERIFIED",
        "reason": (
            "There is not enough strong evidence to verify the claim."
        ),
        "support_count": support_count,
        "contradicts_count": contradicts_count,
    }


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

    # Determine the overall verdict
    verdict_result = determine_verdict(grouped_evidence)

    # Return everything together
    return {
    "claim": claim,
    "verdict": verdict_result["verdict"],
    "reason": verdict_result["reason"],
    "support_count": verdict_result["support_count"],
    "contradiction_count": verdict_result["contradiction_count"],
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

        print("\nOverall verdict:")
        print(result["verdict"])

        print("\nReason:")
        print(result["reason"])

        print("\nStrong evidence counts:")
        print("Supports:", result["support_count"])
        print("Contradicts:", result["contradiction_count"])
        
    except (TypeError, ValueError, RuntimeError) as error:
        print(f"\nError: {error}")