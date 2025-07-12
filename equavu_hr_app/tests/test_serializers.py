from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from equavu_hr_app.models import Candidate, StatusChange, Department, ApplicationStatus
from equavu_hr_app.serializers import (
    CandidateListSerializer,
    CandidateDetailSerializer,
    CandidateCreateSerializer,
    StatusChangeSerializer,
    StatusUpdateSerializer
)
import os


class CandidateSerializerTest(TestCase):
    """Test cases for the Candidate serializers."""

    def setUp(self):
        """Set up test data."""
        # Create a test PDF file
        self.test_file = SimpleUploadedFile(
            "test_resume.pdf",
            b"file content",
            content_type="application/pdf"
        )

        # Create a test candidate
        self.candidate = Candidate.objects.create(
            full_name="Test User",
            email="test@example.com",
            date_of_birth="1990-01-01",
            years_of_experience=5,
            department=Department.IT,
            resume=self.test_file,
            current_status=ApplicationStatus.SUBMITTED
        )

        # Create a status change
        self.status_change = StatusChange.objects.create(
            candidate=self.candidate,
            previous_status=None,
            new_status=ApplicationStatus.SUBMITTED,
            feedback="Application submitted successfully.",
            admin_user="System"
        )

    def tearDown(self):
        """Clean up after tests."""
        # Delete test files
        if self.candidate.resume:
            if os.path.isfile(self.candidate.resume.path):
                os.remove(self.candidate.resume.path)

    def test_candidate_list_serializer(self):
        """Test the CandidateListSerializer."""
        serializer = CandidateListSerializer(self.candidate)
        data = serializer.data

        self.assertEqual(data['full_name'], "Test User")
        self.assertEqual(data['years_of_experience'], 5)
        self.assertEqual(data['department'], Department.IT)
        self.assertEqual(data['current_status'], ApplicationStatus.SUBMITTED)
        self.assertEqual(data['department_display'], "IT")
        self.assertEqual(data['current_status_display'], "Submitted")

    def test_candidate_detail_serializer(self):
        """Test the CandidateDetailSerializer."""
        serializer = CandidateDetailSerializer(self.candidate)
        data = serializer.data

        self.assertEqual(data['full_name'], "Test User")
        self.assertEqual(data['email'], "test@example.com")
        self.assertEqual(data['years_of_experience'], 5)
        self.assertEqual(data['department'], Department.IT)
        self.assertEqual(data['current_status'], ApplicationStatus.SUBMITTED)

        # Check that status changes are included
        self.assertEqual(len(data['status_changes']), 1)
        self.assertEqual(data['status_changes'][0]['new_status'], ApplicationStatus.SUBMITTED)
        self.assertEqual(data['status_changes'][0]['feedback'], "Application submitted successfully.")

    def test_candidate_create_serializer_valid_data(self):
        """Test the CandidateCreateSerializer with valid data."""
        # Create valid data for a new candidate
        valid_data = {
            'full_name': 'New User',
            'email': 'new@example.com',
            'date_of_birth': '1995-05-05',
            'years_of_experience': 3,
            'department': Department.HR,
            'resume': self.test_file
        }

        serializer = CandidateCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_candidate_create_serializer_invalid_data(self):
        """Test the CandidateCreateSerializer with invalid data."""
        # Create invalid data (missing required fields)
        invalid_data = {
            'full_name': 'New User',
            'email': 'new@example.com',
            # Missing date_of_birth
            'years_of_experience': 3,
            'department': Department.HR,
            # Missing resume
        }

        serializer = CandidateCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('date_of_birth', serializer.errors)
        self.assertIn('resume', serializer.errors)

    def test_status_change_serializer(self):
        """Test the StatusChangeSerializer."""
        serializer = StatusChangeSerializer(self.status_change)
        data = serializer.data

        self.assertIsNone(data['previous_status'])
        self.assertEqual(data['new_status'], ApplicationStatus.SUBMITTED)
        self.assertEqual(data['feedback'], "Application submitted successfully.")
        self.assertEqual(data['admin_user'], "System")

    def test_status_update_serializer_valid_data(self):
        """Test the StatusUpdateSerializer with valid data."""
        # Create valid data for a status update
        valid_data = {
            'status': ApplicationStatus.UNDER_REVIEW,
            'feedback': 'Application is under review.'
        }

        serializer = StatusUpdateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_status_update_serializer_invalid_data(self):
        """Test the StatusUpdateSerializer with invalid data."""
        # Create invalid data (invalid status)
        invalid_data = {
            'status': 'INVALID_STATUS',
            'feedback': 'Invalid status.'
        }

        serializer = StatusUpdateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
