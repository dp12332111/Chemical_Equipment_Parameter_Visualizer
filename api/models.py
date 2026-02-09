from django.db import models

class Dataset(models.Model):
    upload_date = models.DateTimeField(auto_now_add=True)
    summary = models.JSONField()  # Stores stats like count, averages, type distribution as JSON
    file = models.FileField(upload_to='datasets/')  # Stores the CSV file
    
    class Meta:
        ordering = ['-upload_date']