import re
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

import mysql.connector
from textblob import TextBlob

# app = Flask(__name__)

# @app.route("/")
# def index():
#     return "Hello World!"


def main():


    # tweets = pd.DataFrame(columns=['id','term','text','sent'])

    term = ''

    while True:
        term = input('Enter a search term: ')
        if term in ['exit', 'e', 'stop']:
            break
        elif term == 'stream':

            strm.append((input('Enter a term to stream: ')))

            getStream(strm[-1])
        else:
            tweets = {
                'term': [],
                'text': [],
                'sent': [],
            }

            getTweets(term, tweets)
            tweet_df = pd.DataFrame.from_dict(tweets)
            print(tweet_df.head(10))
            barChart(tweets)
            
            # tweet_df = pd.DataFrame(columns=['id','term','text','sent'])
            # database_option = input("Save results to database? ")
            # if database_option in ['Y', 'y', 'yes']:
            #     connectSQL(tweets, table='tweets')

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
    stream_tweets['term'].append(strm[-1])
    stream_tweets['text'].append(clean_stream)
    stream_tweets['sent'].append(nbSentiment(clean_stream))


def getStream(strm):
    runtime = int(input('how long should the stream run?: '))
    print('Now istening for: ' + strm)
    stream_listener = tweepStreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=strm, is_async=True)
    time.sleep(runtime)

    print('Time\'s Up! Stream Connection Terminated.')
    stream.disconnect()
    #print (stream_tweets)
    stream_df = pd.DataFrame(stream_tweets)
    print(stream_df.head(10))
    
    barChart(stream_tweets)
    # database_option = input("Save results to database? ")
    # if database_option in ['Y', 'y', 'yes']:
    #     connectSQL(stream_tweets, table='stream')
    
    save_option = input('Save stream results to file? ')
    if save_option in ['Y', 'y', 'yes']:
        saveTweets(stream_tweets)


# def connectSQL(tweets, table):

#     try:
#         connection = mysql.connector.connect(
#             user="root",
#             password="",
#             host="127.0.0.1",
#             database="pytwitter"
#         )

#         cursor = connection.cursor()

#         addtoTable(connection, tweets, table)

#     except connection.Error as err:
#         print(err)


# def addtoTable(connection, tweets, table):
#     x = connection.cursor()
#     for i in range(0, len(tweets['text'])):
#         if table == 'tweets':
#             x.execute('INSERT INTO tweets (search,text,sentiment) VALUES (%s,%s,%s)', (str(
#                 tweets['term'][i]), str(tweets['text'][i]), str(tweets['sent'][i])))

#         elif table == 'stream':
#             x.execute("INSERT INTO streamtweets (search,text,sentiment) VALUES (%s,%s,%s)", (str(
#                 tweets['term'][i]), str(tweets['text'][i]), str(tweets['sent'][i])))

#     connection.commit()


def getTweets(term, tweets):
    for t in tweepy.Cursor(api.search, q='%s -filter:retweets' % term, lang='en', tweet_mode='extended').items(50):
        clean_text = str(cleanTweet(t.full_text))
        if clean_text not in tweets['text']:

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
        return 'Positive'  # positive tweets
    elif tw_sent.sentiment.polarity == 0:
        return 'Neutral'  # negative tweets
    else:
        return 'Negative'  # tweets with no strong polarity


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
    
def barChart(t):
    bar_data = {'pos':0, 'neg':0, 'neu':0}
    bar_sent = []
    for s in t['sent']:
        bar_sent.append(str(s))

    for i in bar_sent:
        if i == 'Positive':
            bar_data['pos'] += 1
        elif i == 'Negative':
            bar_data['neg'] += 1
        else:
            bar_data['neu'] += 1
            
    bkey = bar_data.keys()
    bval = bar_data.values()
    # %matplotlib inline
    plt.bar(bkey,bval)
    plt.show()

if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=8080, debug=True)
    # Twitter API keys
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""

    auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)  # authorises and enables Tweepy API

    stream_tweets = {
        # "id": [],
        "term": [],
        "text": [],
        "sent": []
    }

    strm = []

    fields = ['tweet', 'polarity']
    # findcsv = open(,'r')
    # trainingcsv = findcsv.read()
    traning_data = pd.read_csv('d:/OneDrive/LSBU/Year 3/Final Year Project/mysite/business.csv',
                               usecols=[1, 2], low_memory=True, names=fields, dtype=str)

    csv_df = pd.DataFrame(traning_data)

    print(csv_df)

    tweets_corpus = []
    for i in traning_data['tweet']:
        tweets_corpus.append(cleanTweet(i))

    vect = TfidfVectorizer(stop_words='english', ngram_range=(1, 3))
    X = vect.fit_transform(tweets_corpus)
    y = traning_data['polarity']
    mnb = MultinomialNB(fit_prior=True).fit(X, y)

    def nbSentiment(t):
        t = [t]
        X_test = vect.transform(t)
        y_pred = mnb.predict(X_test)

        t = y_pred[-1]

        # if y_pred == 'Negative':
        #     t = 'Negative'
        # elif y_pred == '4':
        #     t = 'Positive'
        # else:
        #     t = 'Neutral'

        return t

    main()
