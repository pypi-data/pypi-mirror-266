print('''
import pandas as pd
import numpy as np
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')
file_path = 'https://drive.google.com/file/d/1o71dJ3r1-A1QJtzJ4GW5qKk6v3G68vBz/view?usp=drive_link'

# Read csv into as a dataframe
df = pd.read_csv(file_path)

# Display the raw data
df.head()

print(df.columns)

# Droping the unwanted columns
columns_to_drop = ['NBa7we src', 'eaLgGf', 'hCCjke', 'w8nwRe', 'dSlJg', 'znYl0', 'dSlJg 2', 'znYl0 2', 'nM6d2c', 'DZSIDd']
df.drop(columns=columns_to_drop, inplace=True)
df.head()

# Renaming the columns
df.rename(columns={
    'd4r55': 'Name',
    'RfnDt': 'RevPh',
    'rsqaWe': 'Time',
    'wiI7pd': 'Review',
    'wiI7pd 2': 'Reply',
    }, inplace=True)
df.head()

# Extract numbers using regular expressions and create new columns
df['NumReviews'] = df['RevPh'].str.extract(r'(\d+) reviews?').fillna(0).astype(int)
df['NumPhotos'] = df['RevPh'].str.extract(r'(\d+) photos?').fillna(0).astype(int)

# Drop the RevPh column
df.drop('RevPh', axis=1, inplace=True)

# Display the transformed DataFrame
print(df)
print("Number of rows:", df.shape[0])

# Drop rows with NaN values in the 'Name' column
df.dropna(subset=['Name'], inplace=True)
print("Number of rows:", df.shape[0])

# Function to convert time values to number of weeks
# Function to convert time values to number of weeks
def convert_to_weeks(time_str):
    if 'year' in time_str:
        parts = time_str.split()
        if len(parts) > 1 and parts[0].isdigit():
            return int(parts[0]) * 52
        else:
            return 52  # Assuming 'a year ago' implies 1 year
    elif 'month' in time_str:
        parts = time_str.split()
        if len(parts) > 1 and parts[0].isdigit():
            return int(parts[0]) * 4
        else:
            return 4
    elif 'week' in time_str:
        parts = time_str.split()
        if len(parts) > 1 and parts[0].isdigit():
            return int(parts[0]) * 1
        else:
            return 1
    else:
        return 0

# Apply the function to 'Time' column to convert time values to number of weeks
df['Weeks'] = df['Time'].apply(convert_to_weeks)

# Drop the original 'Time' column
df.drop(columns=['Time'], inplace=True)

# Rename the 'Weeks' column to something logical
df.rename(columns={'Weeks': 'Time_in_Weeks'}, inplace=True)

# Display the transformed DataFrame
print(df)

# Function to preprocess text
def preprocess_text(text):
    if pd.notna(text):  # Check for NaN values
        # Convert to string
        text = str(text)
        # Convert text to lowercase
        text = text.lower()
        # Remove punctuation
        text = ''.join([char for char in text if char not in string.punctuation])
        # Tokenize text
        tokens = word_tokenize(text)
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word not in stop_words]
        # Join tokens back into string
        preprocessed_text = ' '.join(filtered_tokens)
        return preprocessed_text
    else:
        return ''

# Preprocess 'Review' column
df['Review'] = df['Review'].apply(preprocess_text)

# Preprocess 'Reply' column
df['Reply'] = df['Reply'].apply(preprocess_text)

# Display the preprocessed DataFrame
print(df)

df.to_csv('processed_data.csv', index=False)

''')