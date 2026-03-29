from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class TaskModel(models.Model):
    """Django model for persisting tasks"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    project = models.CharField(max_length=100, default='General')
    domain = models.CharField(max_length=100, default='General')
    deadline = models.DateTimeField(null=True, blank=True)
    difficulty = models.IntegerField(default=5)
    estimated_effort = models.FloatField(default=1.0)
    importance = models.IntegerField(default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['priority_score', 'created_at']
    
    def __str__(self):
        return self.title

