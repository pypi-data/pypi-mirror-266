print(''' 
import requests
from textblob import TextBlob
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

api_key = "AIzaSyBwJuIfCcu9n9o6tS0dAE2nNo2M0WGQfvs"
video_ids = ["uqskRCuKmeA", "ZDedOr73Qfg", "mKdjycj-7eE"]

def get_comment_sentiment(comment):
    analysis = TextBlob(comment)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity < 0:
        return 'negative'
    else:
        return 'neutral'

for video_id in video_ids:
    comments_list = []

    video_info_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
    video_info_response = requests.get(video_info_url)
    video_info_data = video_info_response.json()
    video_title = video_info_data["items"][0]["snippet"]["title"]
    video_channel = video_info_data["items"][0]["snippet"]["channelTitle"]

    comments_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={api_key}"
    comments_response = requests.get(comments_url)
    comments_data = comments_response.json()
    comments = [item["snippet"]["topLevelComment"]["snippet"]["textOriginal"] for item in comments_data["items"]]

    comments_list.extend(comments)

    comment_text = []
    comment_label = []

    for comment in comments_list:
        comment_text.append(comment)
        t = get_comment_sentiment(comment)
        comment_label.append(t)

    df = pd.DataFrame({"comments": comment_text, "sentiment": comment_label})

    plt.figure(figsize=(8, 6))
    sns.countplot(y='sentiment', data=df, palette='Dark2', hue='sentiment', legend=False)
    plt.title(f"Sentiment Analysis for Video: {video_title} by {video_channel}")
    plt.gca().spines[['top', 'right']].set_visible(False)
    plt.show() ''')