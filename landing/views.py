from django.shortcuts import render
import requests as req
from . import models

import time

# Create your views here.


absolute = True

def landingView(request):
    context = {}
    context['test'] = Twitteruser(350,150)
    udict = {}
    for u in models.TwitterUser.objects.all():
        n = {}
        for other in models.TwitterUser.objects.exclude(username=u.username):
            if not absolute:
                n[other] = (len(models.Follower.objects.filter(follows=models.TwitterUser.objects.get(username=u.username)).filter(follows=models.TwitterUser.objects.get(username=other)))/models.TwitterUser.objects.get(username=u.username).followerCount)*100
            else:
                n[other] = (len(models.Follower.objects.filter(follows=models.TwitterUser.objects.get(username=u.username)).filter(follows=models.TwitterUser.objects.get(username=other))))
            
        udict[u] = n
    context['dict'] = udict
    context['absolute'] = absolute
    return render(request, "landing/circles.html",context)

def generateDataView(request):
    
    m = ""
    if request.method == "POST":
        try:
            m = models.TwitterUser.objects.create(username=request.POST.get('username'))
            m.save()
            
        except Exception as e:
            m = models.TwitterUser.objects.get(username=request.POST.get('username'))
            print("Error: ", e)
            print("USE: ",m)

    context = {}
    if request.method == 'POST':
        headers = {
            'Authorization':'Bearer AAAAAAAAAAAAAAAAAAAAACP0OwEAAAAAKu6o%2FKNL4JwiYWB631z5Mp2hSmU%3D9iB8szeUz2IJrKji1NrDvtuM6xrJdQSeh4wKmdVLKJDvGU2m2Q'
            }

        r = req.get("https://api.twitter.com/1.1/followers/ids.json?cursor=-1&screen_name="+request.POST.get('username')+"&count=5000", headers=headers)
        

        context['follower'] = ""
        context['follower'] += str(r.json()['ids'])
        callCount = 1
        followerCount = 0
        next_cursor = r.json()['next_cursor']
        while next_cursor != 0:
            try:
                callCount = 1
                while next_cursor != 0 and callCount < 15:
                    print("Call: " + str(callCount))
                    r = req.get("https://api.twitter.com/1.1/followers/ids.json?cursor="+str(next_cursor)+"&screen_name="+request.POST.get('username')+"&count=5000", headers=headers)
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
                    f.follows.add(models.TwitterUser.objects.get(username=request.POST.get('username')))
                    f.save()
                
                mm = models.TwitterUser.objects.get(username=request.POST.get('username'))
                mm.followerCount += len(context['follower'].replace('[','').replace("]","").split(","))
                mm.save()

                context['follower'] = ""
            except Exception as e:
                print("Error occured please Wait for Updates")
                time.sleep(60)


        

    return render(request, "landing/generate.html",context)

class Twitteruser:
    def __init__(self, posx, posy):
        self.posx = posx
        self.posy = posy

    weight = [10,5,10]