from django.db import models
from django.contrib.auth.models import User


class FoodDonation(models.Model):
    donor_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    food_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    quantity = models.CharField(max_length=100)
    pickup_address = models.TextField()
    city = models.CharField(max_length=100)
    expiry_time = models.TimeField()
    food_image = models.ImageField(upload_to="food_images/")
    status = models.CharField(
    max_length=20,
    choices=[
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Rejected", "Rejected"),
    ],
    default="Pending"
)
    rejection_reason = models.TextField(
    blank=True,
    null=True
)


def __str__(self):
        return self.food_name


class NGO(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="ngo",
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='ngo_images/')
    status = models.CharField(max_length=20, default='Active')

    def __str__(self):
        return self.name

class DonationRequest(models.Model):
    donor = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    ngo = models.ForeignKey(
        NGO,
        on_delete=models.CASCADE
    )
    food = models.ForeignKey(
        FoodDonation,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Accepted", "Accepted"),
            ("Rejected", "Rejected"),
        ],
        default="Pending"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return f"{self.donor} → {self.ngo}"
    
class HelpSupport(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('DONOR', 'Donor'),
        ('NGO', 'NGO'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message}"
