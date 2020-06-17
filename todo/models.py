from django.db import models
from django.contrib.auth.models import User


class Todo(models.Model):
    title = models.CharField(max_length=150)
    notes = models.TextField(blank=True)
    important = models.BooleanField(default=False)
    createdDate = models.DateTimeField(auto_now_add=True)
    completedDate = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
