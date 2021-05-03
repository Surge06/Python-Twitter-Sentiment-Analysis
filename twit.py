from random import random
import re
import os
from scipy.sparse import data
import tweepy
import time
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import SGDClassifier
from sklearn import metrics

import matplotlib.pyplot as plt

from flask import Flask
import mysql.connector
from textblob import TextBlob

# app = Flask(__name__)

# @app.route("/")
# def index():
#     return "Hello World!"


def main():  # main function that calls in tweets
    # # client = tClient()
    # api=tClient()

    tweets = {
        'term': [],
        'text': [],
        'sent': [],
        # "like": [],
        # "rtwt": []
        # "date":[]
    }

    # tweets = pd.DataFrame(columns=['id','term','text','sent'])

    term = ''

    while True:
        term = input('Enter a search term: ')
        if term in ['exit', 'e', 'stop']:
            break
        elif term == 'stream':

            strm = (input('Enter a term to stream: '))

            getStream(term, strm)
        else:
            getTweets(term, tweets)
            tweet_df = pd.DataFrame.from_dict(tweets)
            print(tweet_df)
            # tweet_df = pd.DataFrame(columns=['id','term','text','sent'])
            database_option = input("Save results to database? ")
            if database_option in ['Y', 'y', 'yes']:
                connectSQL(tweets, table='tweets')

            action = input('Save tweets to file? ')
            if action in ['yes', 'y', 'save']:
                saveTweets(tweets)


class tweepStreamListener(tweepy.StreamListener):

    def on_status(self, status):

        try:
            streamTextSize(status.extended_tweet['full_text'])
        except AttributeError:
            streamTextSize(status.text)

        # if not status.truncated:
        # else:

    def on_error(self, status_code):
        return super().on_error(status_code)


def streamTextSize(text):
    clean_stream = cleanTweet(text)

    # stream_tweets["id"].append(id)
    stream_tweets['term'].append(strm)
    stream_tweets['text'].append(clean_stream)
    stream_tweets['sent'].append(tblobSentiment(clean_stream))


def getStream(term, strm):
    runtime = int(input('how long should the stream run?: '))
    print('Now istening for: ' + term)
    stream_listener = tweepStreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=[strm][-1], is_async=True)
    time.sleep(runtime)

    print('Time\'s Up! Stream Connection Terminated.')
    stream.disconnect()

    stream_df = pd.DataFrame(stream_tweets)
    print(stream_df)

    database_option = input("Save results to database? ")
    if database_option in ['Y', 'y', 'yes']:
        connectSQL(stream_tweets, table='stream')

    save_option = input('Save stream results to file? ')
    if save_option in ['Y', 'y', 'yes']:
        saveTweets(stream_tweets)


def connectSQL(tweets, table):

    try:
        connection = mysql.connector.connect(
            user="root",
            password="",
            host="127.0.0.1",
            database="pytwitter"
        )

        cursor = connection.cursor()

        addtoTable(connection, tweets, table)

    except connection.Error as err:
        print(err)


def addtoTable(connection, tweets, table):
    x = connection.cursor()
    for i in range(0, len(tweets['text'])):
        if table == 'tweets':
            x.execute('INSERT INTO tweets (search,text,sentiment) VALUES (%s,%s,%s)', (str(
                tweets['term'][i]), str(tweets['text'][i]), str(tweets['sent'][i])))

        elif table == 'stream':
            x.execute("INSERT INTO streamtweets (search,text,sentiment) VALUES (%s,%s,%s)", (str(
                tweets['term'][i]), str(tweets['text'][i]), str(tweets['sent'][i])))

    connection.commit()


def getTweets(term, tweets):
    for t in tweepy.Cursor(api.search, q=term, lang='en', tweet_mode='extended').items(300):
        clean_text = str(cleanTweet(t.full_text))
        if clean_text not in tweets['text']:
            if not clean_text.startswith('RT :'):

                # print(clean_text)
                # tweets = tweets.append({'id': t.id, 'term': term, 'text': clean_text , 'sent': tblobSentiment(clean_text)}, ignore_index=True)

                # tweets["id"].append(t.id)
                tweets['term'].append(term)
                tweets['text'].append(clean_text)
                tweets['sent'].append(nbSentiment(clean_text))
                # tweets["like"].append(t.retweeted_status.favorite_count)
                # tweets["rtwt"].append(t.retweeted_status.retweet_count)
                # tweets["date"].append(t.created_at)
                # tweets["geo"].append(t.geo)

    return tweets


def nbTrain(dataset):
    # dataset.head()
    pass
    # X_train_counts = count_vect.fit_transform(dataset.data)
    # X_train_counts.shape


def tblobSentiment(t):  # function for checking tweet polarity
    tw_sent = TextBlob(t)
    if tw_sent.sentiment.polarity > 0:
        return 'positive'  # positive tweets
    elif tw_sent.sentiment.polarity == 0:
        return 'neutral'  # negative tweets
    else:
        return 'negative'  # tweets with no strong polarity


def cleanTweet(t):
    # clean_text=re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", t).split()
    t = re.sub('@[A-Za-z0-9]+', '', t)  # removes Twitter handles/@symbol
    t = re.sub(r'(?:\@|http?\://|https?\://|www)\S+', '', t)  # removes URLs
    t = t.replace("#", "").replace("_", " ")  # remove hashtags and underscores
    t = " ".join(t.split())
    return t


def saveTweets(tweets):
    # try:
    with open(input('Enter a file name: '), 'a+', encoding='utf-8') as tdata:
        tdata.seek(0)
        if tdata.read() == '':
            tdata.write('Search, Tweet, Sentiment\n')

        rows = len(tweets['term'])
        for i in range(0, len(tweets['term'])):
            tdata.write(str(tweets['term'][i]) + ',' + str(tweets['text']
                        [i]).replace(',', ' ')+','+str(tweets['sent'][i])+'\n')

        print('Saved ' + str(rows) + ' rows.\n')

    # # tdata.write(str(tweets["term"][i])+ "," + str(tweets["text"][i]).replace(","," ")+","+str(tweets["sent"][i])+","
    # # +str(tweets["like"][i])+","+str(tweets["rtwt"][i])+"\n")
    #     else:
    #         tdata.write(str(tweets["term"][i]) + "," + str(tweets["text"]
    #                     [i]).replace(",", " ")+","+str(tweets["sent"][i])+"\n")
    tdata.close()
    # except:
    #     print("Error with save.")


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=8080, debug=True)
    # Twitter API keys

    auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)  # authorises and enables Tweepy API

    stream_tweets = {
        # "id": [],
        "term": [],
        "text": [],
        "sent": []
    }

    strm = ''

    fields = ['polarity', 'tweet']
    # findcsv = open(,'r')
    # trainingcsv = findcsv.read()
    traning_data = pd.read_csv('d:/OneDrive/LSBU/Year 3/Final Year Project/mysite/training.1600000.csv',
                               usecols=[5, 0], low_memory=True, names=fields, dtype=str)

    csv_df = pd.DataFrame(traning_data)

    print(csv_df)

    tweets_corpus = []
    for i in traning_data['tweet']:
        tweets_corpus.append(cleanTweet(i))

    vect = TfidfVectorizer(stop_words='english', ngram_range=(1, 1))
    X = vect.fit_transform(tweets_corpus)
    y = traning_data['polarity']
    mnb = MultinomialNB(fit_prior=True).fit(X, y)

    def nbSentiment(t):
        t = [t]
        X_test = vect.transform(t)
        y_pred = mnb.predict(X_test)

        if y_pred == '0':
            t = 'Negative'
        elif y_pred == '4':
            t = 'Positive'
        else:
            t = 'Neutral'

        return t

    # #X,Y = make_classification()
    # gs = GaussianNB()
    # #gs.fit(X_train, y_train)
    # #count_vect = CountVectorizer(stop_words='english', )
    #X_train, X_test, Y_train, Y_test = train_test_split()

    # mnb = MultinomialNB(alpha=1.0, fit_prior=True)

    # tf_vect = TfidfVectorizer(stop_words='english',
    #                           ngram_range=(1, 1), lowercase=False)

    # tfeat = tf_vect.fit_transform(tweets_corpus)

    # X_train, X_test, Y_train, Y_test = train_test_split(
    #     tfeat, traning_data['polarity'], test_size=0.25, random_state=0)

    # mnb.fit(X_train,Y_train)

    # predicted = mnb.predict(X_test)
    # accuracy = metrics.accuracy_score(predicted, Y_test)

    # print(str('{:04.2f}'.format(accuracy*100))+'%')

    # nbTrain(traning_data)

    # pos_data = csv_df[csv_df['polarity'] == 4]
    # neg_data = csv_df[csv_df['polarity'] == 0]
    # neu_data = csv_df[csv_df['polarity'] == 2]

    # positive_tweet = []
    # negative_tweet = []
    # neutral_tweet = []

    # for i, j, k in zip(pos_data, neg_data, neu_data):
    #     positive_tweet = cleanTweet(i)
    #     negative_tweet = cleanTweet(j)
    #     neutral_tweet = cleanTweet(k)

    main()

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

    # tweets= {"text","date","sent"} #"geo",


# strm = []
# dict.fromkeys([,])
# twtext = []
# twsent = []

    # print(df)
    # print(csv_df)
    # csv_group= csv_df.loc[csv_df["polarity"] == "4"]
    # csv_group = csv_df.groupby(csv_df.polarity)
    # pos_data = csv_group.get_group("4")

    # print(pos_data)
    # print(neg_data)
    # groupby(csv_df.columns[1])
    # pos_data = csv_group.get_group("4")
    # neg_data = csv_group.get_group("0")
    # pos_data
    # neg_data
    # print(pos_data,neg_data)


# Authorising the Tweepy API


# class tClient(object):  # twitter client class
#     def __init__(self):  # initialisation method
#         # authentication keys from Twitter dev console
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
#
# textblob analysis tool
# from textblob.classifiers import NaiveBayesClassifier
# from sklearn.naive_bayes import MultinomialNB  # Naive Bayes Analysis

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
