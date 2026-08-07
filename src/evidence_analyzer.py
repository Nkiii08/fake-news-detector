from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from transformers import pipeline

# Load a smaller model used to compare text similarity
similarity_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Load the natural-language inference model
nli_model = pipeline(
    "text-classification",
    model="facebook/bart-large-mnli",
)


def check_relevance(
    claim,
    evidence_text,
    minimum_similarity=0.25,
):
    """
    Check whether the evidence is relevant to the claim.
    """

    # Remove unnecessary spaces
    claim = claim.strip()
    evidence_text = evidence_text.strip()

    # Make sure both inputs contain text
    if not claim:
        raise ValueError("The claim cannot be empty.")

    if not evidence_text:
        raise ValueError("The evidence cannot be empty.")

    # Convert both texts into embeddings
    embeddings = similarity_model.encode(
        [claim, evidence_text],
        convert_to_tensor=True,
    )

    # Compare the two embeddings
    similarity = cos_sim(
        embeddings[0],
        embeddings[1],
    ).item()

    # Decide whether the evidence is relevant
    is_relevant = similarity >= minimum_similarity

    return {
        "is_relevant": is_relevant,
        "similarity": float(similarity),
    }


def analyze_evidence(claim, evidence_text):
    """
    Compare relevant evidence with a claim.

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

    # BART MNLI expects evidence first and claim second
    model_input = f"{evidence_text} </s></s> {claim}"

    # Analyze the relationship
    result = nli_model(model_input)[0]

    # Read the model result
    model_label = result["label"].upper()
    confidence = float(result["score"])

    # Convert model labels into project labels
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


if __name__ == "__main__":

    # Ask the user for a claim
    user_claim = input("Enter a claim: ")

    # Ask the user for evidence
    user_evidence = input("Enter evidence: ")

    try:
        # Check relevance first
        relevance = check_relevance(
            user_claim,
            user_evidence,
        )

        print("\nRelevance analysis:")
        print(
            "Relevant:",
            relevance["is_relevant"],
        )
        print(
            f"Similarity: "
            f"{relevance['similarity']:.2%}"
        )

        # Only run NLI when the evidence is relevant
        if relevance["is_relevant"]:
            analysis = analyze_evidence(
                user_claim,
                user_evidence,
            )

            print("\nEvidence analysis:")
            print(
                "Relationship:",
                analysis["relationship"],
            )
            print(
                f"Confidence: "
                f"{analysis['confidence']:.2%}"
            )

        else:
            print(
                "\nThe evidence was skipped because "
                "it was not relevant enough."
            )

    except ValueError as error:
        print(f"\nError: {error}")