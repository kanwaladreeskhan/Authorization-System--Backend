from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings

class User(AbstractUser):

    email = models.EmailField(
        unique=True
    )

    full_name = models.CharField(
        max_length=255
    )

    USERNAME_FIELD = "email"
    age = models.IntegerField(
    default=18
)
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
    



class RefreshToken(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='refresh_tokens'
    )

    token_hash = models.CharField(
        max_length=255
    )

    family_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )

    issued_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    revoked_at = models.DateTimeField(
        null=True,
        blank=True
    )

    replaced_by = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.email}"

class ResourcePermission(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    resource = models.CharField(
        max_length=100
    )

    can_view = models.BooleanField(
        default=False
    )

    can_edit = models.BooleanField(
        default=False
    )

    def __str__(self):

        return (
            f"{self.user.email}"
            f" - "
            f"{self.resource}"
        )