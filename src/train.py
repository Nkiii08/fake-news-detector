from datasets import load_dataset

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