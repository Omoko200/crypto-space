from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from decimal import Decimal


class User(AbstractUser):
    full_name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    national_id = models.CharField(max_length=50, blank=True, null=True)
    bvn = models.CharField(max_length=11, blank=True, null=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Wallet(models.Model):
    """
    Each user has one wallet storing balances for each crypto.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    btc_balance = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal("0"))
    eth_balance = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal("0"))

    def __str__(self):
        return f"{self.user.username}'s Wallet"


class CryptoTransaction(models.Model):
    """
    Record of Paystack-backed crypto purchase transactions.
    """
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    paystack_ref = models.CharField(max_length=128, unique=True)
    amount_ngn = models.DecimalField(max_digits=12, decimal_places=2)
    crypto_symbol = models.CharField(max_length=10)
    crypto_amount = models.DecimalField(max_digits=20, decimal_places=8)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.crypto_symbol} - {self.status}"



