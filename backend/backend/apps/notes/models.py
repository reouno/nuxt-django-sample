from django.db import models

from backend.apps.accounts.models import CustomUser


class Note(models.Model):
    """Note model"""
    content = models.TextField()
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}: {self.content[:10]}'
