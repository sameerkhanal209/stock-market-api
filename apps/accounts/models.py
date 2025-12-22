from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone as dj_timezone
from django.utils.translation import gettext_lazy as _

import binascii
import os


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("tier", User.Tier.ADMIN)

        return self.create_user(email, password, **extra_fields)

    def active(self):
        """Return only active (non-deactivated) users"""
        return self.filter(is_active=True)


class User(AbstractBaseUser, PermissionsMixin):
    class Tier(models.TextChoices):
        STANDARD = "standard", _("Standard User")
        PREMIUM = "premium", _("Premium User")
        ADMIN = "admin", _("Admin")

    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("full name"), max_length=255, blank=True)
    tier = models.CharField(
        _("account tier"), max_length=20, choices=Tier.choices, default=Tier.STANDARD
    )
    timezone = models.CharField(_("timezone"), max_length=100, default="UTC")
    preferred_currency = models.CharField(_("preferred currency"), max_length=3, default="USD")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)          # Soft deletion
    date_joined = models.DateTimeField(default=dj_timezone.now) 

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["tier"]),
        ]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return f"Profile of {self.user.email}"


class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(32)).decode()

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"