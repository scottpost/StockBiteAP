#==================================================================================================================================
# IMPORTS
#==================================================================================================================================

import tweepy
import sqlite3 as lite
import requests
import urllib
import json
import time
import os
import newspaper
import re
import random
import csv
from nltk.tokenize.punkt import PunktWordTokenizer
from datetime import datetime
from bs4 import BeautifulSoup
from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener

#==================================================================================================================================
# CONFIGURATION
#==================================================================================================================================

#TWITTER API CONFIGURATION
consumer_key = '1xmFquPzhCnuPISoKgqxhwuNf'
consumer_secret = 'C6lqKHIWQWox6GbakacYIntrjk6p59uZTVtacMnirAh1IDqkWf'
access_token = '3831191232-j6ju4yNsyYAyod2GublHVeejOElLS7D6hmouw8Z'
access_secret = 'Cxjirwr5WZNFB368lXv6rwWkN7EcOvU3KDYCUenHK6NWd'
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

#SQLITE 3 CONFIGURATION
con = lite.connect("StockBite.db")
cur = con.cursor()

#SENTIMENT CONFIGURATION
#Words associated with a bullish sentiment
pos = ["buy", "bull", "bullish", "up", "strong", "gaining"]
#Words associated with a bearish sentiment
neg = ["sell", "bear", "bearish", "down", "weak", "losing"] 

#STOCK CONFIGURATION
STOCKS = []
with open('sp500.csv', 'rb') as csvfile:
    csvReader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in csvReader:
        STOCKS.append("$" + row[0])

#WEB SCRAPING CONFIGURATION
ARTICLES = []
BLOGS = []
FORUMS = []

#==================================================================================================================================
# SPAM REMOVAL FUNCTIONS
#==================================================================================================================================

def spamRemover():
    return

def neutralRemover(message):
    # Analyze the sentiment of a bite by comparing it to an array of "positively"
# and "negatively" oriented words.
    buy, sell = 0, 0

    #Tokenize the message into individual words
    tokenizer = PunktWordTokenizer()
    
    #Assign a bullish or bearish sentiment to each word
    for word in tokenizer.tokenize(message):
        if word in pos:
            buy += 1
        if word in neg:
            sell += 1
    
    #Compare total bullish sentiment to total bearish sentiment
    if buy > sell:
        return 1
    
    if buy < sell:
        return -1
    return 0
    


#==================================================================================================================================
# PARSER FUNCTIONS
#==================================================================================================================================

#    _            _ _   _            
#   | |___      _(_) |_| |_ ___ _ __ 
#   | __\ \ /\ / / | __| __/ _ \ '__|
#   | |_ \ V  V /| | |_| ||  __/ |   
#    \__| \_/\_/ |_|\__|\__\___|_| 
#  

#A custom Listener class for Twitter Stream data
class MyListener(StreamListener):

    #Close stream after 1 minute of listening
    timeOut = time.time() + 60
    
    #Called with each succesful query
    def on_status(self, status):
        while time.time() < MyListener.timeOut:
            try:
                #Extract info from status
                message = status.text
                author = status.author.name
                date = "{:%m/%d/%y}".format(status.created_at)
                print "here"
                #Add info to SQL Database
                if neutralRemover(message) != 0:
                    print "really here"
                    cur.execute("INSERT OR IGNORE INTO bites VALUES(?, ?, ?, ?, ?)", ("STREAM", message, author, date, neutralRemover(message)))
                con.commit()
                return True
            except BaseException as e:
                print("Error on_status: %s" % str(e))
        return False

    #Called with each unsuccesful query
    def on_error(self, status):
        print(status)
        return True

#Opens a new Twitter Stream and listens for tweets containing QUERY
def queryTwitterStream(query):
    twitter_stream = Stream(auth, MyListener())
    twitter_stream.filter(track = query[:400])

#Accesses the 30 most recent tweets containing QUERY
def queryTwitterLog(query): 
    for tweet in tweepy.Cursor(api.search, q=query, lang="en").items(50): 
        message = tweet.text
        message = re.sub(r'^https?:\/\/.*[\r\n]*', '', message, flags=re.MULTILINE)
        author = tweet.user.name
        date = "{:%m/%d/%y}".format(tweet.created_at)
        neutral = neutralRemover(message)
        if neutral != 0:
            cur.execute("INSERT OR IGNORE INTO bites VALUES(?, ?, ?, ?, ?)", (query[1:], message, author, date, neutral))
    con.commit()

#        _             _    _____          _ _       
#    ___| |_ ___   ___| | _|_   _|_      _(_) |_ ___ 
#   / __| __/ _ \ / __| |/ / | | \ \ /\ / / | __/ __|
#   \__ \ || (_) | (__|   <  | |  \ V  V /| | |_\__ \
#   |___/\__\___/ \___|_|\_\ |_|   \_/\_/ |_|\__|___/
#                                                     
        
def queryStockTwitsLog(query):
    try:
        url = "https://api.stocktwits.com/api/2/streams/symbol/" + query + ".json"
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        stockTwits = data['messages']
        for twit in stockTwits:
            message = twit['body']
            message = re.sub(r'^https?:\/\/.*[\r\n]*', '', message, flags=re.MULTILINE)
            author = twit['user']['username']
            dateObj = datetime.strptime(twit['created_at'][:10], '%Y-%m-%d')
            date = datetime.strftime(dateObj, "%m/%d/%y")
            neutral = neutralRemover(message)
            if neutral != 0:
                cur.execute("INSERT OR IGNORE INTO bites VALUES(?, ?, ?, ?, ?)", (query, message, author, date, str(neutral))
        con.commit()
    except IndexError:
        print 'Ticker could not be found in the StockTwit database.'
    except KeyError:
        print 'Ticker could not be found in the StockTwit database.'

#   __                            ____                                 
#  / _| ___  _ __ _   _ _ __ ___ / ___|  ___ _ __ __ _ _ __   ___ _ __ 
# | |_ / _ \| '__| | | | '_ ` _ \\___ \ / __| '__/ _` | '_ \ / _ \ '__|
# |  _| (_) | |  | |_| | | | | | |___) | (__| | | (_| | |_) |  __/ |   
# |_|  \___/|_|   \__,_|_| |_| |_|____/ \___|_|  \__,_| .__/ \___|_|   
#                                                     |_|              

def forumScraper():  
    #THE LION
    urlMain = urllib.urlopen("http://www.thelion.com/bin/forum.cgi?cmd=list_all")
    soupMain = BeautifulSoup(urlMain)
    for linkMain in soupMain.find_all('a')[15:30]:
        urlForum = urllib.urlopen("http://www.thelion.com" + linkMain.get("href"))
        soupForum = BeautifulSoup(urlForum)
        for linkForum in soupForum.find_all('a'):
            try:
                urlComment = urllib.urlopen("http://www.thelion.com" + linkForum.get("href"))
                soupComment = BeautifulSoup(urlComment)
                print soupComment.findAll("meta", {"name":"description"})[1]['content']
                message = soupComment.find("span", attrs={"class":"a10"}).text
                date = soupComment.findAll("td", attrs={"class":"r"})[1].text
                author = soupComment.findAll("tr", attrs={"class":"z"})[0].text
                for stock in STOCKS:
                    if stock[1:] in bite:
                        cur.execute("INSERT OR IGNORE INTO bites VALUES(?, ?, ?, ?)", (query[1:], message, author, date))
                        print 'Put StockBite into DB'
            except:
                print 'Could not extract StockBite from source.'
            con.commit()
    
#==================================================================================================================================
# MAIN PARSER FUNCTION
#==================================================================================================================================

#One instance of StockBite parsing - scheduled on an hourly basis through the PythonAnywhere platform
if __name__ == "__main__":
    print 'BEGINNING QUERY...'
    print
    print 'Querying Logs...'
    #Query the twitter & stocktwits logs (30 most recent "important" tweets)
    for stock in STOCKS[300:]:
        try:
            queryTwitterLog(stock)
            print "twit"
            queryStockTwitsLog(stock[1:])
            print 'Queried ' + stock
        except:
            break;
    print 'Querying Twitter Stream...'
    #Listen to the twitter stream for 15 minutes (due to limited CPU usage can't listen for full hour)
    queryTwitterStream(STOCKS)
    print
    print "...QUERY COMPLETED"

#==================================================================================================================================
# 
#==================================================================================================================================