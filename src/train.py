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

