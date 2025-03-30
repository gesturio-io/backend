from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import re
from .password_utils import generate_hash

class LoginType(models.TextChoices):
    email = "email"
    google = "google"
    microsoft = "microsoft"

class UserAuth(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255, null=True, blank=True)
    email_verified = models.BooleanField(default=False)

    login_type = models.CharField(max_length=100, choices=LoginType.choices, default=LoginType.email)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.last_active = timezone.now()
        if self.login_type == LoginType.email:
            check = UserAuth.objects.filter(user_id=self.user_id).exists()
            if not check:
                self.password_hash = generate_hash(self.password_hash)
            
        if self.login_type in [LoginType.google, LoginType.microsoft]:
            self.password_hash = None

        super().save(*args, **kwargs)



class UserProfile(models.Model):
    class Requirement(models.TextChoices): # for priority of sending mails
        other = "Other"
        low = "Just for Fun"
        mid = "Friends"
        high = "Family"
        vhigh = "Work"

    user = models.OneToOneField(UserAuth, on_delete=models.CASCADE, related_name='profile')
    firstname = models.CharField(max_length=255, blank=False, null=False)
    lastname = models.CharField(max_length=255, blank=False,null=False)
    profile_picture = models.URLField(max_length=1000, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    native_language = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=100, blank=False, null=False) 
    daily_goal = models.IntegerField(default=10) # in minutes
    requirement = models.CharField(max_length=100, choices=Requirement.choices, default=Requirement.other)

    def clean(self):
        if self.profile_picture:
            try:
                URLValidator()(self.profile_picture)
            except ValidationError:
                raise ValidationError({'profile_picture': 'Invalid URL format'})
            
        if self.phone_number:   
            cleaned_phone = re.sub(r'\D', '', self.phone_number)
            if len(cleaned_phone) > 10:
                raise ValidationError({'phone_number': 'Phone number must be 10 digits'})
            if not all(c.isdigit() for c in self.phone_number):
                raise ValidationError({'phone_number': 'Phone number can only contain digits'})
            self.phone_number = cleaned_phone

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    