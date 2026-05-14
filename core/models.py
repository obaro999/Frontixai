from django.db import models
from django.contrib.auth.models import User


class Business(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # e.g. "joe-barber"

    def __str__(self):
        return self.name


class BusinessConfig(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=200)
    support_phone = models.CharField(max_length=20)

    def __str__(self):
        return self.business_name


class Appointment(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    date = models.CharField(max_length=50)
    time = models.CharField(max_length=50)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + " - " + self.date + " at " + self.time