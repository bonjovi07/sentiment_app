from django.contrib import admin
from .models import userClass,UserEmployees,UserClients, UserFeedback, Sentiment

# Register your models here.
admin.site.register(userClass)
admin.site.register(UserEmployees)
admin.site.register(UserClients)
admin.site.register(UserFeedback)
admin.site.register(Sentiment)