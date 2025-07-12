from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils import timezone
import os
import uuid


class Department(models.TextChoices):
    IT = 'IT', 'IT'
    HR = 'HR', 'HR'
    FINANCE = 'FINANCE', 'Finance'


class ApplicationStatus(models.TextChoices):
    SUBMITTED = 'SUBMITTED', 'Submitted'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED', 'Interview Scheduled'
    REJECTED = 'REJECTED', 'Rejected'
    ACCEPTED = 'ACCEPTED', 'Accepted'


def resume_upload_path(instance, filename):
    """Generate a unique path for storing resume files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    # Use a temporary UUID if instance.id is not available yet
    folder_name = str(instance.id) if instance.id else str(uuid.uuid4())
    return os.path.join('resumes', folder_name, filename)


class Candidate(models.Model):
    """Model for job candidates"""
    # Note: Using UUIDField for id to ensure unique identification,
    # although sequential IDs could also be used (1,2,3...),
    # it's not recommended for multiple reasons including security and scalability.
    # UUIDs are more suitable for distributed systems and avoid guessable IDs.
    # (which in our case plays a role in checking the application status)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    years_of_experience = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    department = models.CharField(max_length=20, choices=Department.choices)
    resume = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])]
    )
    current_status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.SUBMITTED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.department}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['department']),
            models.Index(fields=['current_status']),
            models.Index(fields=['created_at']),
        ]


class StatusChange(models.Model):
    """Model to track application status changes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='status_changes')
    previous_status = models.CharField(max_length=30, choices=ApplicationStatus.choices, null=True, blank=True)
    new_status = models.CharField(max_length=30, choices=ApplicationStatus.choices)
    feedback = models.TextField(blank=True)
    # The Below field is simplified for admin tracking. This could be replaced with a ForeignKey to a User model.
    admin_user = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.candidate.full_name} - {self.new_status} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['candidate']),
            models.Index(fields=['created_at']),
        ]
