from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AuditableModel(models.Model):
    """
    Abstract base class for auditable models that automatically track
    creation and modification timestamps and users.
    """
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created',
        verbose_name='Created by'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated',
        verbose_name='Updated by'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at'
    )

    class Meta:
        abstract = True

class App(AuditableModel):
    """
    Represents an application in the system.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Feature(AuditableModel):
    """
    Represents a feature within an application.
    """
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['app', 'name']
        ordering = ['app', 'name']

    def __str__(self):
        return f"{self.app.name} - {self.name}"

class Operation(AuditableModel):
    """
    Represents an operation within a feature.
    """
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='operations')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['feature', 'name']
        ordering = ['feature', 'name']

    def __str__(self):
        return f"{self.feature.app.name} - {self.feature.name} - {self.name}"

class RegistrationRequest(AuditableModel):
    """
    Represents a registration request from an external user.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    organization = models.CharField(max_length=200)
    reason = models.TextField(help_text="Why do you need access to the system?")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    comments = models.TextField(
        blank=True,
        help_text="Admin comments on the registration request"
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_registration_requests'
    )

    def __str__(self):
        return f"{self.email} - {self.status}"

    class Meta:
        ordering = ['-created_at']

class PermissionRequest(AuditableModel):
    """
    Represents a permission request from an external app for specific features/operations.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='permission_requests')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='permission_requests')
    operation = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        related_name='permission_requests',
        null=True,
        blank=True
    )
    requesting_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='requested_permissions'
    )
    reason = models.TextField(help_text="Why do you need this permission?")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    comments = models.TextField(
        blank=True,
        help_text="Admin comments on the permission request"
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_permission_requests'
    )

    def __str__(self):
        return f"{self.requesting_user.email} - {self.feature.name} - {self.status}"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['app', 'feature', 'operation', 'requesting_user', 'status']
