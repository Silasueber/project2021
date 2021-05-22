from django.db import models



# Create your models here.
class TwitterUser(models.Model):
    username = models.CharField(max_length=30, unique=True)
    followerCount = models.IntegerField(default=0)
    userid = models.CharField(max_length=30, default="")
    
    def __str__(self):
        return self.username


class Follower(models.Model):
    userid = models.CharField(max_length=30, unique=True)
    follows = models.ManyToManyField(TwitterUser, blank=True)

    def __str__(self):
        return self.userid

class Connections(models.Model):
    fromUser = models.ForeignKey(TwitterUser, on_delete=models.CASCADE, related_name="FROM")
    toUser = models.ForeignKey(TwitterUser, on_delete=models.CASCADE, related_name="TO")
    amount = models.IntegerField(default=0)
    percentage = models.IntegerField(default=0)
    follows = models.BooleanField(default=False)

    def __str__(self):
        return str(self.fromUser)+":"+str(self.toUser)