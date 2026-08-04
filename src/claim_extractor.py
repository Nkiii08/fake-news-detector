import re


def clean_text(text):
    """Remove unnecessary spaces from the input text."""

    # Make sure the input is text
    if not isinstance(text, str):
        raise TypeError("The input must be a string.")

    # Replace repeated spaces and line breaks with one space
    cleaned_text = re.sub(r"\s+", " ", text)

    return cleaned_text.strip()


def extract_claim(text, max_words=40):
    """
    Extract a short searchable claim from the user's text.

    For short input, return the complete text.
    For long input, return the first sentence or first few words.
    """

    # Clean the input
    cleaned_text = clean_text(text)

    # Make sure the input is not empty
    if not cleaned_text:
        raise ValueError("The input text cannot be empty.")

    # Count the words
    words = cleaned_text.split()

    # Keep short claims unchanged
    if len(words) <= max_words:
        return cleaned_text

    # Split the text into sentences
    sentences = re.split(r"(?<=[.!?])\s+", cleaned_text)

    # Use the first sentence if it is useful
    first_sentence = sentences[0].strip()

    if 5 <= len(first_sentence.split()) <= max_words:
        return first_sentence

    # Otherwise, use the first maximum number of words
    shortened_claim = " ".join(words[:max_words])

    return shortened_claim


# Run this section only when testing the file directly
if __name__ == "__main__":

    # Ask the user to enter a claim or article
    user_text = input("Enter a claim or article: ")

    try:
        # Extract the searchable claim
        claim = extract_claim(user_text)

        # Show the result
        print("\nExtracted claim:")
        print(claim)

    except (TypeError, ValueError) as error:
        print(f"\nError: {error}")