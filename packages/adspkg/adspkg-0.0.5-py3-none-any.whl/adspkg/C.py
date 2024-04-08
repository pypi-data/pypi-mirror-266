print(''' 
      
Website : https://reviews.webmd.com/drugs/drugreview-91491-cymbalta-oral?conditionid=&sortval=5&page=140&next_page=true


User Reviews for Cymbalta Oral
Comments on the side effects, benefits, and effectiveness of Cymbalta Oral.


import pandas as pd
from textblob import TextBlob

# Load the CSV file
file_path = "https://drive.google.com/file/d/1yzpNajs3omouq8OpHZeJZJm0ZWTqGJdU/view?usp=sharing"
data = pd.read_csv(file_path)

# Remove columns other than 'description-text' and 'sentiment'
data = data[['description-text']]

# Remove rows with null comments
data.dropna(subset=['description-text'], inplace=True)

# Perform sentiment analysis using TextBlob
sentiments = []
for text in data['description-text']:
    blob = TextBlob(str(text))
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0:
        sentiment = 'Positive'
    elif sentiment_score < 0:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    sentiments.append(sentiment)

# Add the sentiment column to the DataFrame
data['sentiment'] = sentiments

# Display the DataFrame with sentiment analysis results
print(data.head())


import pandas as pd
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report

# Load the CSV file
file_path = "/content/drive/MyDrive/Life of sem 8/SMA/Labs/drug_reviews.csv"
data = pd.read_csv(file_path)

# Remove rows with null comments
data.dropna(subset=['description-text'], inplace=True)

# Define a function to classify comments as negative or non-negative
def classify_sentiment(text):
    blob = TextBlob(str(text))
    sentiment_score = blob.sentiment.polarity
    if sentiment_score < 0:
        return 'Negative'
    else:
        return 'Non-Negative'

# Add the sentiment column to the DataFrame
data['sentiment'] = data['description-text'].apply(classify_sentiment)

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(data['description-text'], data['sentiment'], test_size=0.2, random_state=42)

# Extract features using TF-IDF Vectorizer
tfidf_vectorizer = TfidfVectorizer(max_features=1000)  # You can adjust max_features as per your requirement
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

# Train a classifier (e.g., Linear SVM)
classifier = LinearSVC()
classifier.fit(X_train_tfidf, y_train)

# Evaluate the model
y_pred = classifier.predict(X_test_tfidf)
print(classification_report(y_test, y_pred))

# Define a function to generate suggestions based on negative comments
def suggest_improvements(comment):
    comment_tfidf = tfidf_vectorizer.transform([comment])
    sentiment = classifier.predict(comment_tfidf)[0]
    if sentiment == 'Negative':
        return "Here are some suggestions to improve:\n1. Improve product quality.\n2. Enhance customer service.\n3. Address common complaints proactively.\n4. Provide better instructions or support for product usage."
    else:
        return "Thank you for your feedback!"

# Example usage:
print("-------------------------------------------")
negative_comment = "This med was a disaster for me. I took it for diabetic foot pain and it helped a bit but the side effects were terrible. Within days of starting this drug I starting falling. Over a six month period I fell about 15 times. Also affected my sex life badly. Could not climax while using this terrible drug. finally talked my Dr. into taking me off Cymbalta. My advice is to stay away from this drug !!!"
suggestion = suggest_improvements(negative_comment)
print(suggestion)
print("-------------------------------------------")
negative_comment = "This med was good form me. Its is good."
suggestion = suggest_improvements(negative_comment)
print(suggestion)
print("-------------------------------------------") ''')