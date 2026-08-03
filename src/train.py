import joblib
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

print("Loading dataset...")

dataset = load_dataset("Trinisha/fake_or_real_news")
#show info abt the dataset
print(dataset)

train = dataset["train"] #getting the training data

print("\nColumns:")
print(train.column_names) #printing the column names

print("\nNumber of rows:") 
print(len(train)) #Shows total number of new articles

print("\nFirst article:")
print(train[0]) #printing the first article in the training data

df = train.to_pandas() #converts the dataset into a pandas dataframe

print("\nFirst 5 rows:")
print(df.head()) #printing the first 5 rows of the dataframe

print("\nDataset information:")
print(df.info()) #shows info about each column

print("\nLabel Counts:")
print(df["label"].value_counts()) #shows the count of real and fake in the dataset

# Check if there are any missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Show a random article
print("\nRandom Article:")
print(df.sample(1))

# Show statistics about the dataset
print("\nDataset Statistics:")
print(df.describe())

# Fill missing titles and article text with empty strings
df["title"] = df["title"].fillna("")
df["text"] = df["text"].fillna("")

# Combine the title and article text
df["content"] = df["title"] + " " + df["text"]

# Convert labels into numbers
df["target"] = df["label"].map({
    "FAKE": 0,
    "REAL": 1
})

# Remove rows with empty content
df = df[df["content"].str.strip() != ""]

# Remove duplicate articles
df = df.drop_duplicates(subset=["content"])

# Show the cleaned dataset
print("\nCleaned dataset:")
print(df[["content", "target"]].head())

# Show the number of rows after cleaning
print("\nRows after cleaning:")
print(len(df))

# Select the article text and labels
X = df["content"]
y = df["target"]

#split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

#convert the article into numners
vectorizer = TfidfVectorizer(
    stop_words="english", 
    max_features=5000
    )

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

#create and train the model
model = LogisticRegression(max_iter=1000)
#train the model
model.fit(X_train_tfidf, y_train)

#make predictions on the test set
preditions = model.predict(X_test_tfidf)

#show the models results
print("\nModel Accuracy:")
print(accuracy_score(y_test, preditions))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        preditions,
        target_names=["FAKE", "REAL"]
        )
)


joblib.dump(model, "models/fake_news_model.joblib")
joblib.dump(vectorizer, "models/tfidf_vectorizer.joblib")

print("\nModel and vectorizer saved successfully")

