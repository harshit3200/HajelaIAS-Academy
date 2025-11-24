from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import timedelta


# ---------------- Custom User Manager ----------------
class UserManager(BaseUserManager):
    """Custom user manager to handle email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('is_approved', True)  # ✅ Superusers are always approved

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


# ---------------- Department Model ----------------
class Department(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='department_head'
    )

    def __str__(self):
        return self.name


# ---------------- Custom User Model ----------------
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('student', 'Student'),
    )

    username = None  # Remove username; use email instead
    email = models.EmailField(_('email address'), unique=True)

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )

    # Approval & Rights
    staff_approval_rights = models.BooleanField(default=False)
    admin_approval_rights = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  # ✅ Required for Students & Staff

    # OTP Verification
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_attempts = models.IntegerField(default=0)  # ✅ Track failed OTP attempts

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    # Approval Helpers
    def is_staff_approver(self):
        return self.user_type == 'staff' and self.staff_approval_rights

    def is_admin_approver(self):
        return self.user_type == 'admin' and self.admin_approval_rights

    # OTP Expiry
    def otp_is_expired(self):
        if not self.otp_created_at:
            return True
        return timezone.now() > self.otp_created_at + timedelta(minutes=10)

    # OTP Resend Cooldown
    def can_resend_otp(self):
        if not self.otp_created_at:
            return True
        return timezone.now() > self.otp_created_at + timedelta(minutes=1)

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"


# ---------------- Feature Permissions ----------------
from django.conf import settings
from django.db import models

class FeaturePermission(models.Model):
    FEATURE_CHOICES = [
        # Question Bank
        ("view_question", "View Questions"),
        ("add_question", "Add Questions"),

        # Input Suggestions
        ("add_input_suggestion", "Add Input Suggestion"),
        ("view_input_suggestion", "View Input Suggestion"),

        # Lecture Notes
        ("add_lecture_notes", "Add Lecture Notes"),
        ("view_lecture_notes", "View Lecture Notes"),

        # AI / Tools
        ("generate_image", "Generate Image"),
        ("questcurator", "QuestCurator"),
        ("database_view", "Database View"),
        ("notes_ai", "Notes AI"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feature_permissions"
    )
    feature = models.CharField(max_length=50, choices=FEATURE_CHOICES)

    class Meta:
        unique_together = ("user", "feature")  # ✅ prevent duplicates
        verbose_name = "Feature Permission"
        verbose_name_plural = "Feature Permissions"

    def __str__(self):
        return f"{self.user.email} → {self.get_feature_display()}"
