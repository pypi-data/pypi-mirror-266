print(''' 
import pandas as pd
import numpy as np
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

%matplotlib inline

# Read csv into as a dataframe
df = pd.read_csv('https://drive.google.com/file/d/1IFobwzInzxpsDItDJs6PpcUFUfJ5keDo/view?usp=drive_link', encoding='latin-1')

# Display the raw data
df.head()

print(df.columns)

# Droping the unwanted columns
columns_to_drop = ['store_name', 'category', 'store_address', 'latitude ', 'longitude', 'rating_count']
df.drop(columns=columns_to_drop, inplace=True)
df.head()

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
df['Weeks'] = df['review_time'].apply(convert_to_weeks)

# Drop the original 'Time' column
df.drop(columns=['review_time'], inplace=True)

# Rename the 'Weeks' column to something logical
df.rename(columns={'Weeks': 'review_time_in_Weeks'}, inplace=True)

# Display the transformed DataFrame
df.head()

df['rating'] = df['rating'].str.replace(r'\D', '', regex=True).astype(int)
df.head()

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
df['review'] = df['review'].apply(preprocess_text)

# Display the preprocessed DataFrame
df.head()

print("Number of rows:", df.shape[0])

#Heat Map for missing values
plt.figure(figsize=(17, 5))
sns.heatmap(df.isnull(), cbar=True, yticklabels=False)
plt.xlabel("Column_Name", size=14, weight="bold")
plt.title("Places of missing values in column",fontweight="bold",size=17)
plt.show()

def get_top_n_bigram(corpus, n=None):
    vec = CountVectorizer(ngram_range=(2, 2), stop_words='english').fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:n]

# Printing the top 20 Bigrams
common_words = get_top_n_bigram(df['review'], 20)
print(common_words)

# Instantiate new SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()

# Generate sentiment scores and extract compound score
df['sentiment_score'] = df['review'].apply(lambda x: sid.polarity_scores(x)['compound'])

df.head()

# Count occurrences of each rating value
rating_counts = df['rating'].value_counts()

# Plot a pie chart
plt.figure(figsize=(8, 6))
plt.pie(rating_counts, labels=rating_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Distribution of Ratings')
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()

# Pivot table to count ratings for each week
rating_distribution = df.pivot_table(index='review_time_in_Weeks', columns='rating', aggfunc='size', fill_value=0)

# Plot grouped bar chart
rating_distribution.plot(kind='bar', stacked=True, figsize=(10, 6))
plt.title('Rating Distribution Over Time')
plt.xlabel('Weeks')
plt.ylabel('Number of Ratings')
plt.legend(title='Rating')
plt.xticks(rotation=0)
plt.show()

# Concatenate all reviews into a single string
text = ' '.join(df['review'])

# Generate word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

# Plot word cloud
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.title('Word Cloud of Reviews')
plt.axis('off')  # Hide axis
plt.show()

# Categorize sentiment scores
positive_count = (df['sentiment_score'] > 0).sum()
negative_count = (df['sentiment_score'] < 0).sum()
neutral_count = (df['sentiment_score'] == 0).sum()

# Plot bar graph
plt.figure(figsize=(8, 6))
plt.bar(['Positive', 'Negative', 'Neutral'], [positive_count, negative_count, neutral_count], color=['green', 'red', 'gray'])
plt.title('Sentiment Score Distribution')
plt.xlabel('Sentiment')
plt.ylabel('Count')
plt.show()

''')