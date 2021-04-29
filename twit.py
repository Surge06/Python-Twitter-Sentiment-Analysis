import re
import tweepy
import mysql.connector
from textblob import TextBlob  # textblob analysis tool
from textblob.classifiers import NaiveBayesClassifier
from sklearn.naive_bayes import MultinomialNB  # Naive Bayes Analysis

# import tkinter
# from nltk import text
# import sklearn
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
# from tweepy import cursor
# import PySimpleGUI as pgui
# from tweepy.api import API
# from tweepy import OAuthHandler
# from tweepy.models import SearchResults


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

# tweets= {"text","date","sent"} #"geo",
tweets = {
    "id" : [],
    "term": [],
    "text": [],
    "sent": [],
    # "like": [],
    # "rtwt": []
    # "date":[]
}

# dict.fromkeys([,])
# twtext = []
# twsent = []

# Twitter API keys
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

# Authorising the Tweepy API
auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)  # authorises and enables Tweepy API


try:
    connection = mysql.connector.connect(
        user="", 
        password="",
        host="",
        database=""
        )


    cursor = connection.cursor()
except connection.Error as err:
    print(err)



# class tClient(object):  # twitter client class
#     def __init__(self):  # initialisation method
#         # authentication keys from Twitter dev console
#         consumer_key = "slIzNagtEBxReY55qDsI06TZp"
#         consumer_secret = "seY93Z18dZ1bmpfsdETywIYCbCMR3wb5LMcCXMJ5wmWe8RRLXG"
#         access_token = "836682698596941824-aAkaISzSqP7FNAtnsY4RaYDmR5Yzm0g"
#         access_token_secret = "bCVSlKSYj2BLSWvN64sYeL5hiOt8na1eG0qDc0RyroxS3"

#         # try to authenticate
#         try:
#             # create OAuthHandler object
#             self.auth = OAuthHandler(consumer_key, consumer_secret)
#             # set access token and secret
#             self.auth.set_access_token(access_token, access_token_secret)
#             # create tweepy API object to fetch tweets
#             self.api = tweepy.API(self.auth)
#             #, wait_on_rate_limit=True, wait_on_rate_limit_notify=True
#         except:
#             print("Error: Authentication Failed")


def main():  # main function that calls in tweets
    # # client = tClient()
    # api=tClient()

    term = input("Enter a search term: ")
    getTweets(term)
    print(tweets)
    addtoTable()
    # saveTweets()

class tweepStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

def addtoTable ():
            for i in range(0, len(tweets["text"])):
                x = connection.cursor()
                x.execute("INSERT INTO tweets (search,text,sentiment) VALUES (%s,%s,%s)", (str(tweets["term"][i]),str(tweets["text"][i]),str(tweets["sent"][i])) )

                # print("1 record inserted, ID:", cursor.lastrowid)

                # add_search = ()
                # add_tweet = ()
                # add_sentiment = ()

                connection.commit()


def getStream():
    pass

def getTweets(term):
    for t in tweepy.Cursor(api.search, q=term, lang="en").items(1000):
        if t.id not in tweets["id"]:
            clean_text = str(cleanTweet(t.text))
            tweets["id"].append(t.id)
            tweets["term"].append(term)
            tweets["text"].append(clean_text)
            tweets["sent"].append(tblobSentiment(clean_text))
            # tweets["like"].append(t.retweeted_status.favorite_count)
            # tweets["rtwt"].append(t.retweeted_status.retweet_count)
            # tweets["date"].append(t.created_at)
            # tweets["geo"].append(t.geo)

    return tweets


def tblobSentiment(t):  # function for checking tweet polarity
    tw_sent = TextBlob(t)
    if tw_sent.sentiment.polarity > 0:
        return "positive"  # positive tweets
    elif tw_sent.sentiment.polarity == 0:
        return "neutral"  # negative tweets
    else:
        return "negative"  # tweets with no strong polarity


def cleanTweet(t):
    # clean_text=re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", t).split()
    t = re.sub("@[A-Za-z0-9]+", "", t)  # removes Twitter handles/@symbol
    t = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", t)  # removes URLs
    t = " ".join(t.split())
    return t


def saveTweets():
    # try:
    with open("tweets5.csv", "a+", encoding="utf-8") as tdata:
        tdata.seek(0)
        if tdata.read() == "":
            tdata.write("Tweet,Sentiment,Likes,Retweets\n")
        for i in range(0, len(tweets["text"])):
            tdata.write(str(tweets["term"][i]) + "," + str(tweets["text"]
                        [i]).replace(",", " ")+","+str(tweets["sent"][i])+"\n")

    # tdata.write(str(tweets["term"][i])+ "," + str(tweets["text"][i]).replace(","," ")+","+str(tweets["sent"][i])+","
    # +str(tweets["like"][i])+","+str(tweets["rtwt"][i])+"\n")
        else:
            tdata.write(str(tweets["term"][i]) + "," + str(tweets["text"]
                        [i]).replace(",", " ")+","+str(tweets["sent"][i])+"\n")
    tdata.close()
    # except:
    #     print("Error with save.")

    # # try:
    # for t in tweets:
    #     if t.retweet_count > 0:  # accepting tweets that even have 0 retweets
    #         if t.text not in twtext:
    #             # checks if a tweet isn't in the list
    #             twtext.append(t.text)
    #             twsent.append(tblobSentiment(t.text))

    #         # return twtext, twsent

    # # except tweepy.TweepError as e:
    # #     err = ("Error :" + str(e))

    # length = len(twtext)
    # for i in range(length):
    #     print(twtext[i], twsent[i])

    # saveTweets()

    # posi_tweets = [tweet for tweet in tweets if tweet['sentiment']
    #                == "positive"]  # adds positive tweets
    # nega_tweets = [tweet for tweet in tweets if tweet['sentiment']
    #                == "negative"]  # adds negative tweets
    # neu_tweets = [tweet for tweet in tweets if tweet['sentiment']
    #               == "neutral"]

    # pos_var = len(posi_tweets)  # counting the number of positive tweets
    # neg_var = len(nega_tweets)  # counting the negative tweets
    # neu_var = len(neu_tweets)  # counting neutral tweets
    # #neu_var = pos_var - neg_var

    # print(pos_var)
    # print(neg_var)
    # print(neu_var)

    # print("\nPositive tweets\n")
    # for t in posi_tweets:
    #     print(t['text'])

    # print("\nNegative tweets\n")
    # for t in nega_tweets:
    #     print(t['text'])

    # print("\nNeutral tweets\n")
    # for t in neu_tweets:
    #     print(t['text'])

    # for i in tweets:
    #     print(tweets)
    # def save():
    #     lengh =len(tweets)
    #     with open("tweets2.csv", "a", encoding="utf-8") as savetweets:
    #         for i in range(lengh):
    #             savetweets.write(str(tweets["text"]+"\n"))

    #     savetweets.close

    # save()
if __name__ == "__main__":
    main()
