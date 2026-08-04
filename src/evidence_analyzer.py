from transformers import pipeline

# Load a model trained for natural-language inference
nli_model = pipeline(
    "text-classification",
    model="facebook/bart-large-mnli",
)


def analyze_evidence(claim, evidence_text):
    """
    Compare one piece of evidence with a claim.

    Returns SUPPORTS, CONTRADICTS, or NEUTRAL.
    """

    # Remove unnecessary spaces
    claim = claim.strip()
    evidence_text = evidence_text.strip()

    # Make sure both inputs contain text
    if not claim:
        raise ValueError("The claim cannot be empty.")

    if not evidence_text:
        raise ValueError("The evidence cannot be empty.")

    # BART MNLI expects evidence first and the claim second
    model_input = f"{evidence_text} </s></s> {claim}"

    # Analyze the relationship
    result = nli_model(model_input)[0]

    # Read the model result
    model_label = result["label"].upper()
    confidence = float(result["score"])

    # Convert the model labels into project labels
    label_mapping = {
        "ENTAILMENT": "SUPPORTS",
        "CONTRADICTION": "CONTRADICTS",
        "NEUTRAL": "NEUTRAL",
    }

    relationship = label_mapping.get(
        model_label,
        "NEUTRAL",
    )

    return {
        "relationship": relationship,
        "confidence": confidence,
    }


# Run only when testing this file directly
if __name__ == "__main__":

    # Ask the user for a claim
    user_claim = input("Enter a claim: ")

    # Ask the user for evidence
    user_evidence = input("Enter evidence: ")

    try:
        # Analyze the evidence
        analysis = analyze_evidence(
            user_claim,
            user_evidence,
        )

        # Show the result
        print("\nEvidence analysis:")
        print(
            "Relationship:",
            analysis["relationship"],
        )
        print(
            f"Confidence: "
            f"{analysis['confidence']:.2%}"
        )

    except ValueError as error:
        print(f"\nError: {error}")