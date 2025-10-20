from django.db import models
from django.contrib.auth import get_user_model



User = get_user_model()



# Create your models here.
class KYCVerification(models.Model):
    """KYC Verification Documents"""
    KYC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    DOCUMENT_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('drivers_license', "Driver's License"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kyc_documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_front = models.ImageField(upload_to='kyc_documents/')
    document_back = models.ImageField(upload_to='kyc_documents/', blank=True, null=True)
    selfie = models.ImageField(upload_to='kyc_selfies/')
    
    status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='kyc_reviews'
    )

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"KYC for {self.user.username} - {self.status}"