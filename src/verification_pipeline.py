from src.claim_extractor import extract_claim
from src.evidence_analyzer import analyze_evidence, check_relevance
from src.factcheck_search import search_facts_check
from src.news_search import search_news


def rating_to_relationship(rating):
    """
    Convert a published fact-check rating into
    SUPPORTS, CONTRADICTS, or NEUTRAL.
    """

    # Normalize the rating text
    rating = str(rating).lower().strip()

    # Common words used in false ratings
    false_words = [
        "false",
        "fake",
        "incorrect",
        "misleading",
        "pants on fire",
        "mostly false",
    ]

    # Common words used in true ratings
    true_words = [
        "true",
        "correct",
        "accurate",
        "mostly true",
    ]

    # Return CONTRADICTS if the publisher rated it false
    if any(word in rating for word in false_words):
        return "CONTRADICTS"

    # Return SUPPORTS if the publisher rated it true
    if any(word in rating for word in true_words):
        return "SUPPORTS"

    # Otherwise, we do not have a clear relationship
    return "NEUTRAL"


def analyze_fact_checks(claim, fact_checks):
    """
    Analyze only fact checks that are relevant to the user's claim.
    """

    analyzed_results = []

    for fact_check in fact_checks:

        # Get the reviewed claim
        reviewed_claim = fact_check.get(
            "claim",
            "",
        ).strip()

        # Skip empty reviewed claims
        if not reviewed_claim:
            continue

        # Check whether the reviewed claim is relevant
        relevance = check_relevance(
            claim,
            reviewed_claim,
        )

        # Debug information
        print("\n==============================")
        print("FACT CHECK")
        print("Reviewed claim:")
        print(reviewed_claim)
        print(f"Similarity: {relevance['similarity']:.3f}")
        print(f"Relevant: {relevance['is_relevant']}")

        # Skip unrelated fact checks
        if not relevance["is_relevant"]:
            print("Skipped because it is not relevant.")
            print("==============================")
            continue

        # Get the publisher's existing rating
        rating = fact_check.get(
            "rating",
            "",
        )

        # Convert the publisher rating into our labels
        relationship = rating_to_relationship(
            rating
        )

        # Published fact-check ratings are treated
        # as strong evidence for this first version
        confidence = 1.0

        # Debug information
        print(f"Publisher rating: {rating}")
        print(f"Relationship: {relationship}")
        print(f"Confidence: {confidence:.3f}")
        print("==============================")

        # Store the analyzed fact check
        analyzed_results.append(
            {
                **fact_check,
                "relationship": relationship,
                "confidence": confidence,
                "relevance_score": relevance["similarity"],
            }
        )

    return analyzed_results


def analyze_news_articles(claim, news_articles):
    """
    Analyze only news articles that are relevant to the user's claim.
    """

    analyzed_results = []

    for article in news_articles:

        # Combine title and description
        evidence_text = (
            f"{article.get('title', '')}. "
            f"{article.get('description', '')}"
        ).strip()

        # Skip empty articles
        if not evidence_text:
            continue

        # Check whether the article is relevant
        relevance = check_relevance(
            claim,
            evidence_text,
        )

        # Debug information
        print("\n==============================")
        print("NEWS ARTICLE")
        print(article.get("title", "No title"))
        print(f"Similarity: {relevance['similarity']:.3f}")
        print(f"Relevant: {relevance['is_relevant']}")

        # Skip unrelated articles
        if not relevance["is_relevant"]:
            print("Skipped because it is not relevant.")
            print("==============================")
            continue

        # Analyze the relationship with NLI
        analysis = analyze_evidence(
            claim,
            evidence_text,
        )

        # Debug information
        print(f"Relationship: {analysis['relationship']}")
        print(f"Confidence: {analysis['confidence']:.3f}")
        print("==============================")

        # Store the analyzed article
        analyzed_results.append(
            {
                **article,
                "relationship": analysis["relationship"],
                "confidence": analysis["confidence"],
                "relevance_score": relevance["similarity"],
            }
        )

    return analyzed_results


def group_evidence(fact_checks, news_articles):
    """
    Group analyzed evidence by relationship.
    """

    grouped_results = {
        "supports": [],
        "contradicts": [],
        "neutral": [],
    }

    # Combine all evidence
    all_results = fact_checks + news_articles

    for result in all_results:

        relationship = result["relationship"]

        if relationship == "SUPPORTS":
            grouped_results["supports"].append(
                result
            )

        elif relationship == "CONTRADICTS":
            grouped_results["contradicts"].append(
                result
            )

        else:
            grouped_results["neutral"].append(
                result
            )

    return grouped_results


def determine_verdict(
    grouped_evidence,
    minimum_confidence=0.70,
):
    """
    Determine the overall verdict using strong evidence.
    """

    # Keep strong supporting evidence
    strong_support = [
        item
        for item in grouped_evidence["supports"]
        if item["confidence"] >= minimum_confidence
    ]

    # Keep strong contradicting evidence
    strong_contradictions = [
        item
        for item in grouped_evidence["contradicts"]
        if item["confidence"] >= minimum_confidence
    ]

    support_count = len(strong_support)
    contradiction_count = len(
        strong_contradictions
    )

    # Debug information
    print("\n==============================")
    print("VERDICT DEBUG")
    print(f"Strong supports: {support_count}")
    print(
        f"Strong contradictions: "
        f"{contradiction_count}"
    )
    print("==============================")

    # Conflicting evidence stays unverified
    if (
        support_count > 0
        and contradiction_count > 0
    ):
        return {
            "verdict": "UNVERIFIED",
            "reason": (
                "Strong evidence both supports and "
                "contradicts the claim."
            ),
            "support_count": support_count,
            "contradiction_count": contradiction_count,
        }

    # For testing, one strong source is enough
    if support_count >= 1:
        return {
            "verdict": "SUPPORTED",
            "reason": (
                "Relevant strong evidence supports "
                "the claim."
            ),
            "support_count": support_count,
            "contradiction_count": contradiction_count,
        }

    # For testing, one strong contradiction is enough
    if contradiction_count >= 1:
        return {
            "verdict": "CONTRADICTED",
            "reason": (
                "Relevant strong evidence contradicts "
                "the claim."
            ),
            "support_count": support_count,
            "contradiction_count": contradiction_count,
        }

    # No strong evidence
    return {
        "verdict": "UNVERIFIED",
        "reason": (
            "There is not enough strong and consistent "
            "evidence to verify or contradict the claim."
        ),
        "support_count": support_count,
        "contradiction_count": contradiction_count,
    }


def verify_news(user_text):
    """
    Run the full verification pipeline.
    """

    # Extract the main claim
    claim = extract_claim(
        user_text
    )

    print("\n==============================")
    print("EXTRACTED CLAIM")
    print(claim)
    print("==============================")

    # Retrieve published fact checks
    fact_checks = search_facts_check(
        claim
    )

    print(
        "\nRaw fact checks:",
        len(fact_checks),
    )

    # Retrieve recent news articles
    news_articles = search_news(
        claim
    )

    print(
        "Raw news articles:",
        len(news_articles),
    )

    # Analyze relevant fact checks
    analyzed_fact_checks = analyze_fact_checks(
        claim,
        fact_checks,
    )

    print(
        "\nRelevant fact checks:",
        len(analyzed_fact_checks),
    )

    # Analyze relevant news articles
    analyzed_news_articles = analyze_news_articles(
        claim,
        news_articles,
    )

    print(
        "Relevant news articles:",
        len(analyzed_news_articles),
    )

    # Group all evidence
    grouped_evidence = group_evidence(
        analyzed_fact_checks,
        analyzed_news_articles,
    )

    # Debug grouped evidence
    print("\n==============================")
    print("GROUPED EVIDENCE")
    print(
        "Supports:",
        len(grouped_evidence["supports"]),
    )
    print(
        "Contradicts:",
        len(grouped_evidence["contradicts"]),
    )
    print(
        "Neutral:",
        len(grouped_evidence["neutral"]),
    )
    print("==============================")

    # Determine the final verdict
    verdict_result = determine_verdict(
        grouped_evidence
    )

    # Return everything
    return {
        "claim": claim,
        "verdict": verdict_result["verdict"],
        "reason": verdict_result["reason"],
        "support_count": verdict_result[
            "support_count"
        ],
        "contradiction_count": verdict_result[
            "contradiction_count"
        ],
        "fact_checks": analyzed_fact_checks,
        "news_articles": analyzed_news_articles,
        "evidence": grouped_evidence,
    }


# Run only when testing this file directly
if __name__ == "__main__":

    # Ask the user for a claim
    user_text = input(
        "Enter a claim or article: "
    )

    try:

        # Run the complete pipeline
        result = verify_news(
            user_text
        )

        print("\nExtracted claim:")
        print(
            result["claim"]
        )

        print("\nEvidence summary:")

        print(
            "Supports:",
            len(
                result["evidence"]["supports"]
            ),
        )

        print(
            "Contradicts:",
            len(
                result["evidence"]["contradicts"]
            ),
        )

        print(
            "Neutral:",
            len(
                result["evidence"]["neutral"]
            ),
        )

        print("\nOverall verdict:")
        print(
            result["verdict"]
        )

        print("\nReason:")
        print(
            result["reason"]
        )

        print("\nStrong evidence counts:")

        print(
            "Supports:",
            result["support_count"],
        )

        print(
            "Contradicts:",
            result["contradiction_count"],
        )

    except (
        TypeError,
        ValueError,
        RuntimeError,
    ) as error:

        print(
            f"\nError: {error}"
        )