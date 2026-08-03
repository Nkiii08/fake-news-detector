import joblib

# Load the saved model
model = joblib.load("models/fake_news_model.joblib")

# Load the saved TF-IDF vectorizer
vectorizer = joblib.load("models/tfidf_vectorizer.joblib")


def predict_news(news_text):
    """
    Predict whether a news article is FAKE or REAL.
    Returns the prediction and confidence scores.
    """

    # Convert the article into TF-IDF numbers
    news_tfidf = vectorizer.transform([news_text])

    # Make a prediction
    prediction = model.predict(news_tfidf)[0]

    # Get prediction probabilities
    probabilities = model.predict_proba(news_tfidf)[0]

    return {
        "prediction": prediction,
        "label": "FAKE" if prediction == 0 else "REAL",
        "fake_probability": probabilities[0],
        "real_probability": probabilities[1],
    }


# This only runs when predict.py is executed directly
if __name__ == "__main__":

    # Ask the user to enter a news article
    news_text = input("Enter a news article: ")

    # Get the prediction
    result = predict_news(news_text)

    # Display the result
    print(f"\nPrediction: {result['label']}")
    print(f"FAKE probability: {result['fake_probability']:.2%}")
    print(f"REAL probability: {result['real_probability']:.2%}")