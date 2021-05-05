from django.contrib import admin
from . import models
# Register your models here.

class FollowerAdmin(admin.ModelAdmin):
    search_fields = ['userid']
    
admin.site.register(models.TwitterUser)
admin.site.register(models.Connections)
admin.site.register(models.Follower, FollowerAdmin)
