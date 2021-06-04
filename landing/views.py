from django.shortcuts import render
import requests as req
from . import models

import time

from django.db.models import Max
import networkx as nx
import matplotlib.pyplot as plt
import random
# Create your views here.


absolute = True

def landingView(request):
    
    context = {}
    udict = {}
    followDict = {}
    for u in models.TwitterUser.objects.all():
        n = {}
        fol = {}
        for other in models.TwitterUser.objects.exclude(username=u.username):
            if not absolute:
                n[other] = models.Connections.objects.get(fromUser=u, toUser=other).percentage
            else:
                n[other] = models.Connections.objects.get(fromUser=u, toUser=other).amount
            fol[other] = models.Connections.objects.get(fromUser=u, toUser=other).follows
        udict[u] = n
        followDict[u] = fol
    context['dict'] = udict
    context['absolute'] = absolute
    context['follows'] = followDict

    G = nx.Graph()

    for i in models.TwitterUser.objects.all():
        connections = []
        for con in models.Connections.objects.filter(fromUser=i):
            
            connections.append(con.amount)
        connections.sort(reverse=True)
        for z in range(0,3):
            try:
                max_con = models.Connections.objects.get(fromUser=i, amount=connections[z])
                G.add_edge(max_con.fromUser,max_con.toUser, weight=max_con.amount)
            except:
                print(i, connections[z])
            
        

    # for i in models.Connections.objects.all():
    #     if i.amount > 100:
    #         G.add_edge(i.fromUser,i.toUser, weight=i.amount/1000)
    
    seed = random.randint(0,10000)
    pos = nx.spring_layout(G, k=3, iterations=50, seed=seed)
    # nx.draw_networkx(G, pos=pos)
    # print(pos)
    # plt.show()
    
    context['seed'] = seed
    context['pos'] = pos
    
    return render(request, "landing/circles.html",context)

def whoFollowsWhoView(request):
    
    context = {}
    udict = {}
    followDict = {}
    for u in models.TwitterUser.objects.all():
        n = {}
        fol = {}
        for other in models.TwitterUser.objects.exclude(username=u.username):
            if not absolute:
                n[other] = models.Connections.objects.get(fromUser=u, toUser=other).percentage
            else:
                n[other] = models.Connections.objects.get(fromUser=u, toUser=other).amount
            fol[other] = models.Connections.objects.get(fromUser=u, toUser=other).follows
        udict[u] = n
        followDict[u] = fol
    context['dict'] = udict
    context['absolute'] = absolute
    context['follows'] = followDict


    G = nx.Graph()
    for i in models.Connections.objects.all():
        if i.amount > 1000:
            G.add_edge(i.fromUser,i.toUser, weight=i.amount)
    
    pos = nx.spectral_layout(G)

    context['pos'] = pos


    
    return render(request, "landing/circlesTest.html",context)

 
def getIdFromUsername(Username):
    
    headers = {'Authorization':'Bearer AAAAAAAAAAAAAAAAAAAAABI4PwEAAAAAvL%2BANkwuKEpxiF1P%2ByOCplOkhDo%3D2dFKEI8JkRWEFIhvaVG4JUTX1WYCuV1GCBHsffwTS66kTZxdHA'}
    r = req.get("https://api.twitter.com/1.1/users/show.json?screen_name="+str(Username), headers=headers)
    return r.json()['id']


def AddIdToUsername(Username):
    u = models.TwitterUser.objects.get(username=Username)
    userId = getIdFromUsername(u.username)
    u.userid = userId
    u.save()

def checkFollow(From,To):
    fromId = models.TwitterUser.objects.get(username=From).userid
    t = models.TwitterUser.objects.get(username=To)
    try:
        f = models.Follower.objects.get(userid__contains=' '+str(fromId))
    except:
        return False
    return t in f.follows.all()

def generateDataView(request):
    
    m = ""
    context = {}
    if request.method == "POST":
        l = request.POST.get('username').split(',')
        
        for us in l:
            
            try:
                m = models.TwitterUser.objects.create(username=us)
                m.save()
                
            except Exception as e:
                m = models.TwitterUser.objects.get(username=us)

            m.followerCount = 0
            m.save()
            if request.method == 'POST':
                
                notFinish = True
                while notFinish:
                    try:
                        headers = {
                            'Authorization':'Bearer AAAAAAAAAAAAAAAAAAAAACP0OwEAAAAAKu6o%2FKNL4JwiYWB631z5Mp2hSmU%3D9iB8szeUz2IJrKji1NrDvtuM6xrJdQSeh4wKmdVLKJDvGU2m2Q'
                            
                            }

                        r = req.get("https://api.twitter.com/1.1/followers/ids.json?cursor=-1&screen_name="+us+"&count=5000", headers=headers)
                        
                        
                        context['follower'] = ""
                        context['follower'] += str(r.json()['ids'])
                        callCount = 1
                        followerCount = 0
                        next_cursor = r.json()['next_cursor']
                        notFinish = False
                    except:

                        print("Error occured please Wait for Updates...")
                        c = 10
                        while c > 0:
                            print("Next try in: " + str(c) + " Seconds")
                            c -= 1
                            time.sleep(1)
                if next_cursor != 0:
                    while next_cursor != 0:
                        try:
                            callCount = 1
                            while next_cursor != 0 and callCount < 15:
                                
                                r = req.get("https://api.twitter.com/1.1/followers/ids.json?cursor="+str(next_cursor)+"&screen_name="+us+"&count=5000", headers=headers)
                                print("Call: " + str(callCount))
                                context['follower'] += str(r.json()['ids'])
                                next_cursor = r.json()['next_cursor']
                                callCount += 1
                            
                            i = 0
                            for l in context['follower'].replace('[','').replace("]","").split(","):
                                print("Working on ID("+str(i)+"): ",l)
                                i += 1
                                try:
                                    f = models.Follower.objects.get(userid=l)
                                except:
                                    f = models.Follower.objects.create(userid=l)
                                f.follows.add(models.TwitterUser.objects.get(username=us))
                                f.save()
                            
                            mm = models.TwitterUser.objects.get(username=us)
                            mm.followerCount += len(context['follower'].replace('[','').replace("]","").split(","))
                            mm.save()

                            context['follower'] = ""
                        except Exception as e:
                            print("Error occured please Wait for Updates...")
                            c = 10
                            while c > 0:
                                print("Next try in: " + str(c) + " Seconds")
                                c -= 1
                                time.sleep(1)
                else:
                    i = 0
                    for l in context['follower'].replace('[','').replace("]","").split(","):
                            print("Working on ID("+str(i)+"): ",l)
                            i += 1
                            try:
                                f = models.Follower.objects.get(userid=l)
                            except:
                                f = models.Follower.objects.create(userid=l)
                            f.follows.add(models.TwitterUser.objects.get(username=us))
                            f.save()
                            
                            mm = models.TwitterUser.objects.get(username=us)
                            mm.followerCount = len(context['follower'].replace('[','').replace("]","").split(","))
                            mm.save()
    return render(request, "landing/generate.html",context)

def calculateView(request):
    context = {}
    if request.method == "POST":
         for u in models.TwitterUser.objects.all():
            AddIdToUsername(u.username)
            for other in models.TwitterUser.objects.exclude(username=u.username):
                print(u.username," : ", other.username)
                try:
                    m = models.Connections.objects.get(fromUser=u, toUser=other)
                except:
                    m = models.Connections.objects.create(fromUser=u, toUser=other)

                m.follows = checkFollow(u.username,other.username)
                m.percentage = (len(models.Follower.objects.filter(follows=models.TwitterUser.objects.get(username=u.username)).filter(follows=models.TwitterUser.objects.get(username=other)))/models.TwitterUser.objects.get(username=u.username).followerCount)*100
                m.amount = (len(models.Follower.objects.filter(follows=models.TwitterUser.objects.get(username=u.username)).filter(follows=models.TwitterUser.objects.get(username=other))))
                m.save()
                context['info'] = "success!"
    return render(request, "landing/calculateData.html", context)
       