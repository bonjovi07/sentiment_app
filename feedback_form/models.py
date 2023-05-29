from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class userClass(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=((1, 'admin'), (0, 'office')), default=0)

    def __str__(self):
        return self.user.username
    
class UserEmployees(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)
    position = models.CharField(max_length=100, default='')
    office = models.CharField(max_length=100)
    office_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
class UserClients(models.Model):
    client_name = models.CharField(max_length=100)
    client_agency = models.CharField(max_length=100, default='N/A')
    client_token_link = models.CharField(max_length=100)
    client_email = models.EmailField(blank=True)
    purpose_of_visit = models.TextField(blank=True)
    client_visit_date = models.DateTimeField(auto_now_add=True)
    expiration_time = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    attending_staff = models.ForeignKey(UserEmployees, on_delete=models.CASCADE)

    @property
    def is_expired(self):
        return timezone.now() > self.expiration_time

    def __str__(self):
        return self.client_name
    
class UserFeedback(models.Model):
    feedback_courtesy = models.IntegerField()
    feedback_quality = models.IntegerField()
    feedback_timeless = models.IntegerField()
    feedback_efficiency = models.IntegerField()
    feedback_cleanliness = models.IntegerField()
    feedback_comfort = models.IntegerField()
    feedback_comments = models.TextField()
    feedback_client = models.ForeignKey(UserClients, on_delete=models.CASCADE)
    feedback_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Feedback for {self.feedback_client}"
    
class Sentiment(models.Model):
    sentiment_feedback = models.ForeignKey(UserFeedback, on_delete=models.CASCADE)
    sentiment_analysis = models.CharField(max_length=50)
    user_sentiment_analysis = models.CharField(max_length=50, null=True, blank=True)
    negative_prob = models.FloatField()
    positive_prob = models.FloatField()
    neutral_prob = models.FloatField()

    def __str__(self):
        return f"Sentiment for Feedback #{self.sentiment_feedback.id}"