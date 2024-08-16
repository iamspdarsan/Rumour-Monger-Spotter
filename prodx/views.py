
import sqlite3 as sql
import time

import lib.classifier as classifier
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from lib.factapi import factApi
from lib.reporter import report
from lib.scraper import scrap


class Prodx:
   
    def main_page(req):
        userip = req.META.get('HTTP_X_FORWARDED_FOR', req.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
        print("User IP: ",userip)
        return render(req,"mainpage.html")
    
    
    @csrf_exempt
    def getlink(req):
        if req.method == 'POST':
            link=str(req.POST['tweetlink'])
            
            dtime=str(time.ctime().split(' '))
            print("Time is ",time.ctime())
            
            data=scrap(link)#it returns dictionary    
            file='db.sqlite3'
            dbcon=sql.connect(file)
            cursur=dbcon.cursor()

            try:
                cursur.execute("INSERT INTO prodx"+
                    "(reporttime,tweetlink,tweetcontent,userid,username,userloc,tweetloc,ip,tag) VALUES(?,?,?,?,?,?,?,?,?)", 
                    [dtime,link,data['content'],data['userid'],data['username'],data['userloc'],data['tweetloc'],'0',data['tag']])
            except sql.OperationalError:  
                cursur.execute('CREATE TABLE "prodx" (	"id" INTEGER,"reporttime" TEXT,"tweetlink" TEXT,"tweetcontent"	TEXT,'+
	            '"userid" TEXT,"username" TEXT,"userloc" TEXT,"tweetloc" TEXT,"ip" TEXT,"tag" TEXT,PRIMARY KEY("id" AUTOINCREMENT))')
            finally:
                dbcon.commit()
                cursur.close()
                dbcon.close()

            factData = factApi(data['tag'])
            categorized_dataset = classifier.categorize_data(factData)
            report(categorized_dataset,data['content'])
        return HttpResponseRedirect('/')
