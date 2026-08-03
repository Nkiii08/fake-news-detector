import streamlit as stl

from src.predict import predict_news

# Add the page title
stl.title("Fake News Detector")

# Explain the purpose of the app
stl.write(
    "This app uses a machine learning model to predict whether a news article "
    "resembles FAKE or REAL articles from the training dataset."
)

# Create a large text box
news_text = stl.text_area(
    "Enter news text:",
    height=250
)

# Run when the user clicks the button
if stl.button("Check Article"):

    # Make sure the text box isn't empty
    if not news_text.strip():
        stl.warning("Please enter a news article.")

    else:
        # Get the prediction
        result = predict_news(news_text)

        # Show the prediction
        if result["prediction"] == 0:
            stl.error("Prediction: FAKE")
        else:
            stl.success("Prediction: REAL")

        # Show confidence
        stl.write(f"FAKE probability: {result['fake_probability']:.2%}")
        stl.write(f"REAL probability: {result['real_probability']:.2%}")

        # Explain the limitations
        stl.info(
            "This model recognizes patterns learned from the training dataset. "
            "It does not independently verify whether a news article is factually true."
        )