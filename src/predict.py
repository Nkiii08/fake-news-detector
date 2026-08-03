import joblib
import pandas as pd

#load the saved model
model = joblib.load("models/fake_news_model.joblib")

#load the saved tfidf vectorizer
vectorizer = joblib.load("models/tfidf_vectorizer.joblib")

#Ask the user to enter a news arcticle
news_text = input("Enter a news article: ")

#convert the news article into numbers
news_tfidf = vectorizer.transform([news_text])

#make a prediction
prediction = model.predict(news_tfidf)[0]

# Get probabilities for FAKE and REAL
probabilities = model.predict_proba(news_tfidf)[0]

fake_probability = probabilities[0]
real_probability = probabilities[1]

# Show the result
if prediction == 0:
    print("\nPrediction: FAKE")
else:
    print("\nPrediction: REAL")

print(f"FAKE probability: {fake_probability:.2%}")
print(f"REAL probability: {real_probability:.2%}")

#convert the article into term frequency-inverse document frequency (TF-IDF) numbers
news_tfidf = vectorizer.transform([news_text])

#make a prediction
prediction = model.predict(news_tfidf)[0]

#get the prediction probabilities for FAKE and REAL
probabilities = model.predict_proba(news_tfidf)[0]

#store the probabilities for FAKE and REAL
fake_probability = probabilities[0]
real_probability = probabilities[1]

#show the prediction
if prediction == 0:
    print("\nPrediction: FAKE")
else:
    print("\nPrediction: REAL")

#show the confidence for both classes
print(f"FAKE probability: {fake_probability:.2%}")
print(f"REAL probability: {real_probability:.2%}")
