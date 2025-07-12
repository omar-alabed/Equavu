"""
Serializers for the HR application models.
"""
from rest_framework import serializers
from .models import Candidate, StatusChange, Department, ApplicationStatus
from django.core.validators import FileExtensionValidator
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class StatusChangeSerializer(serializers.ModelSerializer):
    """Serializer for the StatusChange model."""

    class Meta:
        model = StatusChange
        fields = ['id', 'previous_status', 'new_status', 'feedback', 'admin_user', 'created_at']
        read_only_fields = ['id', 'created_at']


class CandidateListSerializer(serializers.ModelSerializer):
    """Serializer for listing candidates (admin view)."""
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    current_status_display = serializers.CharField(source='get_current_status_display', read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'full_name', 'date_of_birth', 'years_of_experience',
                  'department', 'department_display', 'current_status',
                  'current_status_display', 'created_at']
        read_only_fields = ['id', 'created_at']


class CandidateDetailSerializer(serializers.ModelSerializer):
    """Serializer for candidate details including status changes."""
    status_changes = StatusChangeSerializer(many=True, read_only=True)
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    current_status_display = serializers.CharField(source='get_current_status_display', read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'full_name', 'email', 'date_of_birth', 'years_of_experience',
                  'department', 'department_display', 'current_status',
                  'current_status_display', 'created_at', 'updated_at', 'status_changes']
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_status']


class CandidateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new candidate with resume upload."""
    resume = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])]
    )

    class Meta:
        model = Candidate
        fields = ['full_name', 'email', 'date_of_birth', 'years_of_experience',
                  'department', 'resume']

    def validate_resume(self, value):
        """Validate resume file size."""
        if value.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File size exceeds the limit of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)}MB."
            )
        return value

    def validate_years_of_experience(self, value):
        """Validate years of experience is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        return value

    def validate_department(self, value):
        """Validate department is one of the allowed choices."""
        if value not in [choice[0] for choice in Department.choices]:
            raise serializers.ValidationError(
                f"Department must be one of: {', '.join([choice[0] for choice in Department.choices])}")
        return value


class StatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating a candidate's application status."""
    status = serializers.ChoiceField(choices=ApplicationStatus.choices)
    feedback = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        """Validate status is one of the allowed choices."""
        if value not in [choice[0] for choice in ApplicationStatus.choices]:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join([choice[0] for choice in ApplicationStatus.choices])}")
        return value
