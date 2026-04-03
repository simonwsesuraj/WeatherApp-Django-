from django.db import models

class SearchHistory(models.Model):
    city_name = models.CharField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    description = models.TextField()
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city_name} at {self.searched_at.strftime('%Y-%m-%d  %H:%M')}"