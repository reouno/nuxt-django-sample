"""Master table definitions of Account app"""
from django.db import models


class GenderMaster(models.Model):
    """Gender master table"""
    id = models.CharField(primary_key=True, unique=True, blank=False, max_length=30, editable=False)

    def __str__(self):
        return f'{self.id}'
