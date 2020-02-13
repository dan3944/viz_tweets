import argparse
import matplotlib.pyplot as plt
import os
import pandas as pd
import tweepy

consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# download tweets to csv so we don't need query the API every time
def download_tweets(handle):
    df = pd.DataFrame([
        {
            'text': tweet.full_text,
            'retweets': tweet.retweet_count,
            'favorites': tweet.favorite_count,
            'interactions': tweet.retweet_count + tweet.favorite_count,
        }
        for page in tweepy.Cursor(api.user_timeline, id=handle, tweet_mode='extended', count=200).pages()
        for tweet in page
        if not tweet.full_text.startswith('RT @')  # exclude retweets
    ])

    df.to_csv(f'{handle}/tweets.csv')


# read tweets from csv into dataframe
def read_tweets(handle):
    return pd.read_csv(f'{handle}/tweets.csv', index_col=0)


# generate visualization and save it to a file
def viz_top_tweets(tweets_df, handle):
    tweets_df \
        .sort_values('interactions') \
        .tail(50) \
        .assign(text=lambda df: df['text'].str.replace('\n', ' \\n ')) \
        .plot.barh(x='text', y=['retweets', 'favorites'], figsize=(20, 18)) \
        .set(xlabel='Interactions', ylabel='Tweet', title=f'@{handle}\'s Most Popular Tweets')

    plt.savefig(f'{handle}/tweets.png', bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('handle', help='The twitter handle to analyze')
    parser.add_argument('--redownload', action='store_true',
                        help='Whether to redownload the given user\'s tweets (if they\'ve already been downloaded)')
    args = parser.parse_args()

    if not os.path.isdir(args.handle):
        os.mkdir(args.handle)

    if args.redownload or not os.path.isfile(f'{args.handle}/tweets.csv'):
        download_tweets(args.handle)

    tweets_df = read_tweets(args.handle)
    viz_top_tweets(tweets_df, args.handle)
