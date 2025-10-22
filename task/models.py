from django.db import models
from django.contrib.auth import get_user_model



User = get_user_model()





class Task(models.Model):
    """Tasks for users to complete"""
    TASK_TYPE_CHOICES = [
        ('daily', 'Daily Task'),
        ('referral', 'Referral Task'),
        ('kyc', 'KYC Task'),
        ('social', 'Social Media Task'),
        ('custom', 'Custom Task'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES)
    reward_tokens = models.DecimalField(max_digits=10, decimal_places=4)
    claimed_users = models.ManyToManyField(User,blank=True)
    is_active = models.BooleanField(default=True)
    required_action = models.CharField(max_length=255, blank=True)
    images = models.ImageField(upload_to='task/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


User = get_user_model()

# # Create your models here.
# class UserTask(models.Model):
#     """Track user task completion"""
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('active', 'Active'),
#         ('completed', 'Completed'),
#         ('claimed', 'Claimed'),
#     ]
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tasks')
#     task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='user_completions')
    
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     started_at = models.DateTimeField(null=True, blank=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
#     claimed_at = models.DateTimeField(null=True, blank=True)
    
#     proof_url = models.URLField(blank=True, null=True)
#     notes = models.TextField(blank=True)

#     class Meta:
#         unique_together = ['user', 'task']
#         ordering = ['-completed_at']

#     def __str__(self):
#         return f"{self.user.username} - {self.task.title} - {self.status}"