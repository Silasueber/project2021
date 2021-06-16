from django.shortcuts import render
import requests as req
from . import models

import time

from django.db.models import Max
import networkx as nx
import matplotlib.pyplot as plt
import random

import landing.functions as func
# Create your views here.


absolute = True


def calculate_Position(neighboor_count):
    G = nx.Graph()

    for i in models.TwitterUser.objects.all():
        connections = []
        for con in models.Connections.objects.filter(fromUser=i):
            
            connections.append(con.amount)
        connections.sort(reverse=True)
        for z in range(0,neighboor_count):
            try:
                max_con = models.Connections.objects.get(fromUser=i, amount=connections[z])
                weight = (max_con.amount/connections[0])*100
                G.add_edge(max_con.fromUser,max_con.toUser, weight=max_con.percentage)
            except:
                print(i, connections[z])
            
    seed = random.randint(0,10000)
    pos = nx.spring_layout(G, k=1.5, iterations=50, seed=seed)


    return seed, pos

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

    game= {}
    for u in models.TwitterUser.objects.all():
        try:
            game[u] = u.game.all()[0].color
        except:
            game[u] = "#ffffff"

    context['game'] = game

    if request.method == "POST":
        seed, pos = calculate_Position(int(request.POST.get('basedRange')))
        context['based'] = request.POST.get('basedRange')
    else:
        seed, pos = calculate_Position(3)
        context['based'] = 3

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


# Creates a Databank entry for the Twitterusers 
# and updates the Follower Databank with their follower
def generate_TwitterUser_Entry(users):
        

        #initilize Variables
        m = ""
        follower_String = ""

        #iterates through all Users
        for us in users:
            
            #set m to the model, if it doesn't exist, it gets created
            m, created = models.TwitterUser.objects.get_or_create(username=us)

            print(m)

            #the Followercount gets set to 0 and the model gets saved
            m.followerCount = 0
            m.save()
            
            #cheks if the request to the database was succesfull
            notFinish = True
            while notFinish:
                try:
                    #initilize header and request URL
                    headers = {
                        'Authorization':'Bearer AAAAAAAAAAAAAAAAAAAAACP0OwEAAAAAKu6o%2FKNL4JwiYWB631z5Mp2hSmU%3D9iB8szeUz2IJrKji1NrDvtuM6xrJdQSeh4wKmdVLKJDvGU2m2Q'
                        }

                    r = req.get("https://api.twitter.com/1.1/followers/ids.json?cursor=-1&screen_name="+us+"&count=5000", headers=headers)
                    
                    #Clears the follower_String and adds the new ids to it
                    follower_String = ""
                    follower_String += str(r.json()['ids'])

                    #Set the callCount and set the next_cursor to value from the request
                    callCount = 1
                    next_cursor = r.json()['next_cursor']

                    #If it got so far everything worked fine and the while-loop is finish
                    notFinish = False
                except:

                    #If an Error occured, more requests were made then the API allows
                    #So we print a Feedback to the user, After 10 Seconds
                    #We try again
                    print("Error occured please Wait for Updates...")
                    for c in range(0,10):
                        print("Next try in: " + str(10-c) + " Seconds")
                        time.sleep(1)
                    
            if next_cursor != 0:
                while next_cursor != 0:
                    try:
                        callCount = 1
                        while next_cursor != 0 and callCount < 15:
                            
                            r = req.get("https://api.twitter.com/1.1/followers/ids.json?cursor="+str(next_cursor)+"&screen_name="+us+"&count=5000", headers=headers)
                            print("Call: " + str(callCount))
                            follower_String += str(r.json()['ids'])
                            next_cursor = r.json()['next_cursor']
                            callCount += 1
                        
                        i = 0
                        for l in follower_String.replace('[','').replace("]","").split(","):
                            i += 1
                            try:
                                f = models.Follower.objects.get(userid=l)
                            except:
                                f = models.Follower.objects.create(userid=l)
                            f.follows.add(models.TwitterUser.objects.get(username=us))
                            f.save()
                        
                        mm = models.TwitterUser.objects.get(username=us)
                        mm.followerCount += len(follower_String.replace('[','').replace("]","").split(","))
                        mm.save()

                        follower_String = ""
                    except Exception as e:
                        print("Error occured please Wait for Updates...")
                        c = 10
                        while c > 0:
                            print("Next try in: " + str(c) + " Seconds")
                            c -= 1
                            time.sleep(1)
            else:
                i = 0
                
                #Set Progressbar
                func.printProgressBar(0, len(follower_String.replace('[','').replace("]","").split(",")), prefix = 'Progress:', suffix = 'Complete', length = 50)

                
                for l in follower_String.replace('[','').replace("]","").split(","):
                        i += 1
                        func.printProgressBar(i, len(follower_String.replace('[','').replace("]","").split(",")), prefix = 'Progress:', suffix = 'Complete', length = 50)
                        
                        try:
                            f = models.Follower.objects.get(userid=l)
                        except:
                            f = models.Follower.objects.create(userid=l)
                        f.follows.add(models.TwitterUser.objects.get(username=us))
                        f.save()
                        
                        mm = models.TwitterUser.objects.get(username=us)
                        mm.followerCount = len(follower_String.replace('[','').replace("]","").split(","))
                        mm.save()
            


# calculates all the Connections between the Streamer
# and updates the Database or creates a new entry
def calculate_Connections():
    
    #Set Progressbar
    func.printProgressBar(0, len(models.TwitterUser.objects.all())*(len(models.TwitterUser.objects.all())-1), prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    #set counter
    progess_counter = 0
    for u in models.TwitterUser.objects.all():
            AddIdToUsername(u.username)
            for other in models.TwitterUser.objects.exclude(username=u.username):
                progess_counter += 1
                func.printProgressBar(progess_counter, len(models.TwitterUser.objects.all())*(len(models.TwitterUser.objects.all())-1), prefix = 'Progress:', suffix = 'Complete', length = 50)
                try:
                    m = models.Connections.objects.get(fromUser=u, toUser=other)
                except:
                    m = models.Connections.objects.create(fromUser=u, toUser=other)

                m.follows = checkFollow(u.username,other.username)
                m.percentage = (len(models.Follower.objects.filter(follows=models.TwitterUser.objects.get(username=u.username)).filter(follows=models.TwitterUser.objects.get(username=other)))/models.TwitterUser.objects.get(username=u.username).followerCount)*100
                m.amount = (len(models.Follower.objects.filter(follows=models.TwitterUser.objects.get(username=u.username)).filter(follows=models.TwitterUser.objects.get(username=other))))
                m.save()
    return True

def generateDataView(request):
    
    
    context = {}
    if request.method == "POST":
        users = request.POST.get('username').split(',')
        generate_TwitterUser_Entry(users)

    return render(request, "landing/generate.html",context)



def calculateView(request):
    context = {}
    if request.method == "POST":
        if calculate_Connections():
            context['info'] = "success!"
    return render(request, "landing/calculateData.html", context)
       