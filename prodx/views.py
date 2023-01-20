from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import time
import sqlite3 as sql
import tweepy
import requests as req
import json
import pandas as pd
from .classifier import *

api_key = ""
api_secret_key = ""
access_token = ""
access_token_secret = ""
# authorization of consumer key and consumer secret
auth = tweepy.OAuthHandler(api_key, api_secret_key)
# set access to user's access key and access secret 
auth.set_access_token(access_token, access_token_secret)  
# calling the api 
api = tweepy.API(auth)
def scrap(link):  
    tweetid=link[link.find('status/')+len('status/'):link.find('?')]
    tweet=api.get_status(tweetid)
    #print(tweet.user)
    print("\nUser ID - ",tweet.user.screen_name)#user_id
    print("Tweet content - ",tweet.text)
    try:
        tag=tweet.entities['hashtags'][0]['text']
        print("Tag is",tag)#first tag
    except IndexError:
        print("hashtag is not available")
        tag=0
    tweetloc=0
    userloc=0
    try:
        print("User profile location is ",tweet.user.location)
        userloc=tweet.user.location
    except:
        pass
    try:
        print("User state is",tweet.place.name)#place_dist_state
        tweetloc=tweet.place.name
    except:
        pass
    print("Tweet posted on ",tweet.created_at)#tweet_posted_at
    print("Tweet link - ",link)
    #print(tweetid)
    result={
        'userid':tweet.user.screen_name,
        'username':tweet.user.name,
        'userloc':userloc,
        'createdat':tweet.created_at,
        'tweetloc':tweetloc,
        'content':tweet.text,
        'tag':tag,
    }
    return result

class DataMan:

    def __init__(self):
        self.file='db.sqlite3'
        self.dbcon=sql.connect(self.file)
        self.cursur=self.dbcon.cursor()

# Create your views here.
class Prodx:
    def __init__(self):
        pass

    def main_page(req):
        print("User IP",req.META.get('HTTP_X_FORWARDED_FOR', req.META.get('REMOTE_ADDR', '')).split(',')[0].strip())
        return render(req,"mainpage.html")
    
    
    @csrf_exempt
    def getlink(req):
        if req.method == 'POST':
            link=str(req.POST['tweetlink'])
            #tweet link is 19digit
            dtime=str(str(time.ctime()).split(' '))
            print("Time is ",time.ctime())
            data=scrap(link)#it returns dictionary    
            file='db.sqlite3'
            dbcon=sql.connect(file)
            cursur=dbcon.cursor()

            try:
                cursur.execute("INSERT INTO prodx"+
                    "(reporttime,tweetlink,tweetcontent,userid,username,userloc,tweetloc,ip,tag) VALUES(?,?,?,?,?,?,?,?,?)", 
                    [dtime,link,data['content'],data['userid'],data['username'],data['userloc'],data['tweetloc'],'0',data['tag']])
            except sql.OperationalError as ex:
                print(ex)                
                cursur.execute('CREATE TABLE "prodx" (	"id" INTEGER,"reporttime" TEXT,"tweetlink" TEXT,"tweetcontent"	TEXT,'+
	            '"userid" TEXT,"username" TEXT,"userloc" TEXT,"tweetloc" TEXT,"ip" TEXT,"tag" TEXT,PRIMARY KEY("id" AUTOINCREMENT))')
            dbcon.commit()
            cursur.close()
            dbcon.close()
            dataset = categorizeData(apicall(data['tag']))
            report(dataset,data['content'])
        return HttpResponseRedirect('/')


def apicall(query):
    parameters={
        'key':'',
        'query':query,
        'languageCode':'en-US',
        'pageSize':1000,
    }
    response = req.get('https://factchecktools.googleapis.com/v1alpha1/claims:search',params=parameters)
    #print("status code",response.status_code)
    claims=json.loads(response.content.decode('utf-8'))['claims']
    print(f'\n\n{len(claims)} claims are available')
    return claims
    
def categorizeData(data):    
    #divide true and false
    trueset=[]
    falseset=[]
    otherset=[]
    for i in data:
        if i['claimReview'][0]['textualRating'].lower() == 'true':
            trueset.append(i)
        elif i['claimReview'][0]['textualRating'].lower() == 'false':
            falseset.append(i)
        else:
            otherset.append(i)
    print("\n======Data are Grouped======")
    print(f'{len(trueset)} - data are true')
    print(f'{len(falseset)} - data are false')
    print(f'{len(otherset)} - data are others\n')
    truetext =[] 
    falsetext =[]
    #extracting text that claimed as true
    for text in trueset:
        truetext.append(text['text'])
    #extracting text that claimed as false
    for text in falseset:
        falsetext.append(text['text'])
    tdf=pd.DataFrame(list(zip(len(truetext)*['true'],truetext)),columns=['label', 'text'])
    fdf=pd.DataFrame(list(zip(len(falsetext)*['false'],falsetext)),columns=['label', 'text'])
    dataset = pd.concat([tdf,fdf],axis=0)
    return dataset

def report(dataset,text):
    cleandata(dataset)
    transformed=[]
    for i in dataset['text']:
        transformed.append(transform_text(i))
    dataset['transformed_text'] = transformed
    accuarcy, precision = build_model(dataset)
    print("Model has been built")
    print("Predicting.....")
    print("Accuracy is ",accuarcy)
    classify(text)
    