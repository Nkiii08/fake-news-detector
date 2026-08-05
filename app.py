import streamlit as stl

from src.predict import predict_news
from src.verification_pipeline import verify_news

# Configure the browser tab
stl.set_page_config(
    page_title="Fake News Detector",
    layout="centered",
)


# Add the application title
stl.title("Fake News Detector")

# Explain what the application does
stl.write(
    "Enter a news claim, headline, or article below. "
    "The app will show a writing-pattern prediction and search "
    "for current evidence related to the claim."
)


# Create a text box
news_text = stl.text_area(
    "Enter news text:",
    height=250,
    placeholder="Paste a news claim, headline, or article here...",
)


# Run when the user clicks the button
if stl.button("Check Article"):

    # Make sure the text box is not empty
    if not news_text.strip():
        stl.warning("Please enter a news claim or article.")

    else:
        # Show the baseline machine-learning result
        stl.subheader("Writing-pattern baseline")

        try:
            # Get the TF-IDF model prediction
            baseline_result = predict_news(news_text)

            # Show the prediction
            if baseline_result["prediction"] == 0:
                stl.error("Prediction: FAKE")
            else:
                stl.success("Prediction: REAL")

            # Show the probabilities
            stl.write(
                f"FAKE probability: "
                f"{baseline_result['fake_probability']:.2%}"
            )

            stl.write(
                f"REAL probability: "
                f"{baseline_result['real_probability']:.2%}"
            )

            # Explain the baseline limitation
            stl.info(
                "This baseline model only recognizes writing patterns "
                "learned from its training dataset. It does not independently "
                "verify whether the information is factually correct."
            )

        except (ValueError, RuntimeError, FileNotFoundError) as error:
            stl.error(f"Baseline prediction failed: {error}")

        # Separate the two systems visually
        stl.divider()

        # Show the evidence-based verification result
        stl.subheader("Real-time evidence verification")

        try:
            # Run the complete verification pipeline
            verification_result = verify_news(news_text)

            # Show the extracted claim
            stl.write("**Extracted claim:**")
            stl.write(verification_result["claim"])

            # Get the verdict
            verdict = verification_result["verdict"]

            # Show the verdict
            if verdict == "SUPPORTED":
                stl.success("Verdict: SUPPORTED")

            elif verdict == "CONTRADICTED":
                stl.error("Verdict: CONTRADICTED")

            else:
                stl.warning("Verdict: UNVERIFIED")

            # Show the reason
            stl.write("**Reason:**")
            stl.write(verification_result["reason"])

            # Show evidence counts
            col1, col2 = stl.columns(2)

            with col1:
                stl.metric(
                    "Strong supporting evidence",
                    verification_result["support_count"],
                )

            with col2:
                stl.metric(
                    "Strong contradicting evidence",
                    verification_result["contradicts_count"],
                )

            # Show published fact checks
            stl.subheader("Published fact checks")

            fact_checks = verification_result["fact_checks"]

            if not fact_checks:
                stl.info(
                    "No matching published fact checks were found."
                )

            else:
                for number, fact_check in enumerate(
                    fact_checks,
                    start=1,
                ):
                    title = fact_check.get(
                        "review_title",
                        f"Fact-check result {number}",
                    )

                    with stl.expander(title):
                        stl.write(
                            f"**Claim reviewed:** "
                            f"{fact_check.get('claim', 'Not available')}"
                        )

                        stl.write(
                            f"**Rating:** "
                            f"{fact_check.get('rating', 'Not available')}"
                        )

                        stl.write(
                            f"**Publisher:** "
                            f"{fact_check.get('publisher', 'Not available')}"
                        )

                        stl.write(
                            f"**Relationship:** "
                            f"{fact_check.get('relationship', 'Not available')}"
                        )

                        confidence = fact_check.get(
                            "confidence",
                            0,
                        )

                        stl.write(
                            f"**Analysis confidence:** "
                            f"{confidence:.2%}"
                        )

                        url = fact_check.get("url")

                        if url and url != "Not available":
                            stl.link_button(
                                "Open fact-check",
                                url,
                            )

            # Show recent related news
            stl.subheader("Recent related news")

            news_articles = verification_result["news_articles"]

            if not news_articles:
                stl.info(
                    "No recent related news articles were found."
                )

            else:
                for number, article in enumerate(
                    news_articles,
                    start=1,
                ):
                    title = article.get(
                        "title",
                        f"News article {number}",
                    )

                    with stl.expander(title):
                        stl.write(
                            f"**Source:** "
                            f"{article.get('source', 'Not available')}"
                        )

                        stl.write(
                            f"**Published:** "
                            f"{article.get('published_at', 'Not available')}"
                        )

                        stl.write(
                            f"**Relationship:** "
                            f"{article.get('relationship', 'Not available')}"
                        )

                        confidence = article.get(
                            "confidence",
                            0,
                        )

                        stl.write(
                            f"**Analysis confidence:** "
                            f"{confidence:.2%}"
                        )

                        description = article.get(
                            "description",
                            "No description available.",
                        )

                        stl.write(description)

                        url = article.get("url")

                        if url and url != "Not available":
                            stl.link_button(
                                "Open article",
                                url,
                            )

            # Explain the limitation of the evidence system
            stl.warning(
                "A missing fact-check or news result does not prove that a "
                "claim is true. UNVERIFIED means the system did not find "
                "enough strong and consistent evidence."
            )

        except (TypeError, ValueError, RuntimeError) as error:
            stl.error(f"Verification failed: {error}")