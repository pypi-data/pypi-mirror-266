#############################################################
#
#  Author: Sebastian Maurice, PhD
#  Copyright by Sebastian Maurice 2018
#  All rights reserved.
#  Email: Sebastian.maurice@otics.ca
#
#############################################################

import json, urllib
import requests
import csv
import os
import imp
import re
import urllib.request
import asyncio
import validators
from urllib.parse import urljoin
from urllib.parse import urlsplit
import aiohttp
from aiohttp import ClientSession
import async_timeout



def formaturl(maindata,host,microserviceid,prehost,port):

    if len(microserviceid)>0:    
      mainurl=prehost + "://" + host +  ":" + str(port) +"/" + microserviceid + "/?hyperpredict=" + maindata
    else:
      mainurl=prehost + "://" + host + ":" + str(port) +"/?hyperpredict=" + maindata
        
    return mainurl
    
async def tcp_echo_client(message, loop,host,port,usereverseproxy,microserviceid):

    hostarr=host.split(":")
    hbuf=hostarr[0]
   # print(hbuf)
    hbuf=hbuf.lower()
    domain=''
    if hbuf=='https':
       domain=host[8:]
    else:
       domain=host[7:]
    host=domain  

    if usereverseproxy:
        geturl=formaturl(message,host,microserviceid,hbuf,port) #host contains http:// or https://
        message="GET %s\n\n" % geturl 

    reader, writer = await asyncio.open_connection(host, port, loop=loop)
    try:
      mystr=str.encode(message)
      writer.write(mystr)
      datam=''
      while True:
        data = await reader.read(1024)
      #  print(data)
        datam=datam+data.decode("utf-8")
       # print(datam)
        if not data:
           break
        
        await writer.drain()
   #   print(datam)  
      prediction=("%s" % (datam))
      writer.close()
    except Exception as e:
      print(e)
      return e
    
    return prediction

def hyperpredictions(pkey,theinputdata,host,port,username,algoname='',seasonname='',usereverseproxy=0,microserviceid='',password='123',company='otics',email='support@otics.ca',maadstoken='123'):

    if pkey=='' or theinputdata == '' or host== '' or port=='' or username=='':
        print("ERROR: Please specify pkey, theinputdata, host, port, username")
        return

    if '_nlpclassify' not in pkey:
      theinputdata=theinputdata.replace(",",":")
    else:  
      buf2 = re.sub('[^a-zA-Z0-9 \n\.]', '', theinputdata)
      buf2=buf2.replace("\n", "").strip()
      buf2=buf2.replace("\r", "").strip()
      theinputdata=buf2

    if usereverseproxy:
       theinputdata=urllib.parse.quote(theinputdata)
  
    value="%s,[%s],%s,%s,%s,%s,%s,%s" % (pkey,theinputdata,maadstoken,username,company,email,algoname,seasonname)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_client(value, loop,host,port,usereverseproxy,microserviceid))
    #loop.close()
    return val

async def tcp_echo_clienttrain(message, loop,host,port,microserviceid,timeout=1200):

    #if len(microserviceid)>0:
#    geturl=formaturltrain(message,host,microserviceid,hbuf,port) #host contains http:// or https://
 #   message="%s" % geturl 
    try:
     with async_timeout.timeout(timeout):
      async with ClientSession() as session:
        html = await fetch(session,message)
        await session.close()
        return html
    except Exception as e:
     pass   

def genpkey(username,filename):
     pkey = ""
     chars_to_remove= [" ", "(", ")","%","$","&","#","+","=","\\","@",".","/",":","*","?","\"","|","<",">"]
     
     if username != "" and filename != "":
         sc = set(chars_to_remove)
         for i in sc:
           filename = filename.replace(i, '_')

     pkey = username + "_" + filename

     return pkey

#pkey=genpkey('admin','aesopowerdemand.csv')
#print(pkey)
    
def hypertraining(host,port,filename,dependentvariable,removeoutliers=0,hasseasonality=0,summer='6,7,8',winter='11,12,1,2',shoulder='3,4,5,9,10',trainingpercentage=70,shuffle=0,deepanalysis=0,username='admin',timeout=1200,company='otics',password='123',email='support@otics.ca',usereverseproxy=0,microserviceid='',maadstoken='123',mode=0):

# curl "http://localhost:5595?hypertraining=1&mode=0&username=admin&company=otics&email=support@otics.ca&filename=aesopowerdemand.csv&removeoutliers=0&
#hasseasonality=0&dependentvariable=AESO_Power_Demand&summer=6,7,8&winter=11,12,1,2&shoulder=3,4,5,9,10&trainingpercentage=70&shuffle=0&deepanalysis=0"
#maads.hypertraining(maadstoken,host,port,filename,dependentvariable,username='admin',mode=0,timeout=180,company='otics',removeoutliers=0,hasseasonality=0,summer='6,7,8',winter='11,12,1,2',shoulder='3,4,5,9,10',trainingpercentage=70,shuffle=0,deepanalysis=0,password='123',email='support@otics.ca',usereverseproxy=0,microserviceid='')

    if host=='' or port=='' or filename=='' or dependentvariable == '':
        print("Please enter host,port,filename,dependentvariable")
        return ""

    print("Please wait...this could take 3-5 minutes") 
    
    url = "%s:%s/?hypertraining=1&" % (host,port)
    params = {'mode': str(mode), 'username': username,'company': company,'email': email,'filename': filename,'removeoutliers': str(removeoutliers),'hasseasonality': str(hasseasonality),'dependentvariable': dependentvariable,'summer': summer,'winter': winter,'shoulder': shoulder, 'trainingpercentage': str(trainingpercentage),'shuffle': str(shuffle),'deepanalysis': str(deepanalysis)}
    mainurl = url + urllib.parse.urlencode(params)

    print(mainurl)
    try:
      value="%s" % (mainurl)
      loop = asyncio.get_event_loop()
      val=loop.run_until_complete(tcp_echo_clienttrain(value, loop,host,port,microserviceid,timeout))
    except IOError as e: 
      if e.errno == errno.EPIPE: 
        pass

    if val == None:
       pkey=genpkey(username,filename)
       val="{\"AlgoKey\":\"" + pkey + "\", \"BrokenPipe\":\"Broken pipe exception was caught - this may happen due to network issues. The system will finish - use the AlgoKey and check the 'exception' folder for your algorithm JSON, and check PDFREPORTS folder for your pdf.\"}" 
       return val
    
  #  loop.close()
    return val

def algodescription(host,port,pkey,timeout=300,usereverseproxy=0,microserviceid=''):
    if host=='' or port=='' or pkey=='':
        print("Please enter host,port, and PKEY (this is the key you eceived from the hypertraining funtion.)")
        return ""

    url = "%s:%s/?algoinfo=1&pkey=%s" % (host,port,pkey)
    mainurl = url

    print(mainurl)
  
    value="%s" % (mainurl)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clienttrain(value, loop,host,port,microserviceid,timeout))
 #   loop.close()
    return val

def rundemo(host,port,demotype=1,timeout=1200,usereverseproxy=0,microserviceid=''):

    print("Please wait...this could take 3-5 minutes") 
    url = "%s:%s/?rundemo=%s" % (host,port,str(demotype))
    mainurl = url

    print(mainurl)
  
    value="%s" % (mainurl)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clienttrain(value, loop,host,port,microserviceid,timeout))
#    loop.close()
    return val

def abort(host,port=10000):

    url = "%s:%s/?abort=1" % (host,port)
    mainurl = url

    print(mainurl)
  
    value="%s" % (mainurl)
    loop = asyncio.get_event_loop()
    val=loop.run_until_complete(tcp_echo_clienttrain(value, loop,host,port,''))
#    loop.close()
    return val

#########################################################

async def fetch(client,url):
    async with client.get(url) as resp:
        assert resp.status == 200
        return await resp.text()

