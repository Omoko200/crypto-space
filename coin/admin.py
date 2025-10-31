from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Wallet, CryptoTransaction

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Extends Django’s built-in UserAdmin to work with our custom User model.
    You can later add KYC fields here if needed.
    """
    list_display = ("username", "email", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)


# ---------------------------
# Wallet Admin
# ---------------------------
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "btc_balance", "eth_balance")
    search_fields = ("user__username",)
    readonly_fields = ("user",)


# ---------------------------
# Crypto Transaction Admin
# ---------------------------
@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "crypto_symbol",
        "amount_ngn",
        "crypto_amount",
        "status",
        "paystack_ref",
        "created_at",
    )
    list_filter = ("status", "crypto_symbol", "created_at")
    search_fields = ("user__username", "paystack_ref")
    readonly_fields = ("created_at",)


# ---------------------------
# Generic Transaction Log Admin
# ---------------------------
# @admin.register(Transaction)
# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ("user", "crypto_symbol", "amount_ngn", "reference", "status", "created_at")
#     list_filter = ("status", "crypto_symbol")
#     search_fields = ("user__username", "reference")
#     readonly_fields = ("created_at",)