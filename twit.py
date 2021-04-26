import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob  # text analysis tool
# import atlastk
# import tkinter
import sklearn
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# import PySimpleGUI as pgui
from tweepy.api import API

from tweepy.models import SearchResults


# pgui.theme ("Reddit")
# layout = [
#             [pgui.Text("Hello, welcome to the Python Twitter Analysis Tool!")],
#             [[pgui.Text("Enter a search term: "), pgui.InputText()]],
#             [pgui.Button("Search"),pgui.Button("Exit")]
#          ]


# window = pgui.Window("PyTwitter Tool", layout, margins=(640, 480))

# while True:
#     event, values = window.read()
#     if event == "OK" or event == pgui.WIN_CLOSED:
#         break

# window.close()


class tClient(object):  # twitter client class
    def __init__(self):  # initialisation method
        # authentication keys from Twitter dev console


        # try to authenticate
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def sanitise(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())
        # function to sanitise tweets

    def get_setntiment(self, tweet):  # function for checking tweet polarity
        tw_sent = TextBlob(self.sanitise(tweet))
        if tw_sent.sentiment.polarity > 0:
            return "positive"  # positive tweets
        elif tw_sent.sentiment.polarity == 0:
            return "neutral"  # negative tweets
        else:
            return "negative"  # tweets with no strong polarity

    def gather(self, query, count=10):
        # an emptry list for storing tweets to call back later
        tweets = []

        try:
            gt = self.api.search(q=query, count=count)
            for tweet in gt:
                pt = {}
                pt["text"] = tweet.text
                pt["sentiment"] = self.get_setntiment(tweet.text)

                if tweet.retweet_count > 0:  # accepting tweets that even have 0 retweets
                    if pt not in tweets:
                        # checks if a tweet isn't in the list
                        tweets.append(pt)
                    else:
                        tweets.append(pt)
            return tweets
        except tweepy.TweepError as e:
            err = ("Error :" + str(e))


def main():  # main function that calls in tweets
    class inputClass(object):
        def __init__(self, term):
            self.term = term

    term = input("Enter a search term: ")

    api = tClient()
    # test term to search for, as it is a polarising topic
    tweets = api.gather(query=term, count=200)

    posi_tweets = [tweet for tweet in tweets if tweet['sentiment']
                   == "positive"]  # adds positive tweets
    nega_tweets = [tweet for tweet in tweets if tweet['sentiment']
                   == "negative"]  # adds negative tweets
    neu_tweets = [tweet for tweet in tweets if tweet['sentiment']
                  == "neutral"]
                  
    pos_var = len(posi_tweets)  # counting the number of positive tweets
    neg_var = len(nega_tweets)  # counting the negative tweets
    neu_var = len(neu_tweets)  # counting neutral tweets
    #neu_var = pos_var - neg_var

    print(pos_var)
    print(neg_var)
    print(neu_var)

    print("\nPositive tweets\n")
    for t in posi_tweets:
        print(t['text'])

    print("\nNegative tweets\n")
    for t in nega_tweets:
        print(t['text'])

    print("\nNeutral tweets\n")
    for t in neu_tweets:
        print(t['text'])

    def save():

        with open("tweets.csv", "a", encoding="utf-8") as savetweets:
            for i in tweets:
                savetweets.write(str(i["text"]+"\n"))

        savetweets.close

    save()


if __name__ == "__main__":
    main()
