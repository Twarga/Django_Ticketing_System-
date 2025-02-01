from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-one relationship with the User model
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Additional field for the phone number
    bio = models.TextField(blank=True, null=True)  # Field for a short bio
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Field for profile picture

    def __str__(self):
        return f'{self.user.username} Profile'


class Ticket(models.Model):
    # Status choices for the ticket
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    # Priority choices for the ticket
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    # Category choices for the ticket
    CATEGORY_CHOICES = [
        ('billing', 'Billing'),
        ('technical', 'Technical'),
        ('general', 'General'),
    ]

    title = models.CharField(max_length=255)  # The title of the ticket
    description = models.TextField()  # A detailed description of the ticket issue
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new'
    )  # Current status of the ticket
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default='medium'
    )  # Priority level (low, medium, high)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='general'
    )  # Ticket category (billing, technical, etc.)
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tickets'
    )  # The customer who created the ticket
    agent = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets'
    )  # The agent assigned to handle the ticket
    created_at = models.DateTimeField(auto_now_add=True)  # Ticket creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Ticket last updated timestamp

    def __str__(self):
        return self.title

    def escalate_ticket(self):
        """
        Method to automatically escalate the ticket if it's not handled within 48 hours.
        If the ticket is not resolved and is past the 48-hour limit, escalate to high priority.
        """
        if self.status != 'resolved' and self.created_at + timedelta(hours=48) < self.updated_at:
            self.priority = 'high'  # Escalate priority to high
            self.save()

    def update_status(self, new_status):
        """
        Method to update the status of the ticket.
        - 'new' for newly created tickets
        - 'in_progress' when an agent starts working on it
        - 'resolved' when the issue is solved
        - 'closed' when the ticket is completed
        """
        self.status = new_status
        self.save()

    def assign_agent(self, agent):
        """
        Method to assign an agent to the ticket.
        This updates the 'agent' field and can be used by the admin or during ticket handling.
        """
        self.agent = agent
        self.save()

    def close_ticket(self):
        """
        Method to close the ticket once it's resolved and completed. This sets the status to 'closed'.
        """
        if self.status == 'resolved':
            self.status = 'closed'
            self.save()


class TicketHistory(models.Model):
    ACTION_CHOICES = [
        ('status_change', 'Status Change'),
        ('comment', 'Comment'),
        ('feedback', 'Feedback'),
    ]
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')  # The ticket this history record relates to
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)  # Action type: status change, comment, or feedback
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who performed the action (customer, agent, or admin)
    comment = models.TextField(null=True, blank=True)  # Optional: comment related to the action (can be empty for status changes)
    previous_status = models.CharField(max_length=20, null=True, blank=True)  # Previous status before status change (can be null if not a status change)
    new_status = models.CharField(max_length=20, null=True, blank=True)  # New status after status change (can be null if not a status change)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the action occurred
    
    def __str__(self):
        return f"Action on {self.ticket.title} by {self.user.username} at {self.created_at}"
    


class Feedback(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='feedback')  # The ticket this feedback relates to
    customer = models.ForeignKey(User, on_delete=models.CASCADE)  # The customer who provided feedback
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1 to 5 (1 is poor, 5 is excellent)
    comment = models.TextField(blank=True)  # Optional comment providing more details about the feedback
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the feedback was given
    
    def __str__(self):
        return f"Feedback for {self.ticket.title} by {self.customer.username}"





@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()