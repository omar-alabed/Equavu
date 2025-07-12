from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from equavu_hr_app.models import Candidate, StatusChange, Department, ApplicationStatus
import os


class CandidateModelTest(TestCase):
    """Test cases for the Candidate model."""

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

    def tearDown(self):
        """Clean up after tests."""
        # Delete test files
        if self.candidate.resume:
            if os.path.isfile(self.candidate.resume.path):
                os.remove(self.candidate.resume.path)

    def test_candidate_creation(self):
        """Test that a candidate can be created with valid data."""
        self.assertEqual(self.candidate.full_name, "Test User")
        self.assertEqual(self.candidate.email, "test@example.com")
        self.assertEqual(self.candidate.years_of_experience, 5)
        self.assertEqual(self.candidate.department, Department.IT)
        self.assertEqual(self.candidate.current_status, ApplicationStatus.SUBMITTED)
        self.assertTrue(self.candidate.resume)

    def test_candidate_str_representation(self):
        """Test the string representation of a candidate."""
        expected_str = f"{self.candidate.full_name} - {self.candidate.department}"
        self.assertEqual(str(self.candidate), expected_str)

    def test_candidate_ordering(self):
        """Test that candidates are ordered by created_at in descending order."""
        # Create another candidate
        second_candidate = Candidate.objects.create(
            full_name="Another User",
            email="another@example.com",
            date_of_birth="1995-01-01",
            years_of_experience=3,
            department=Department.HR,
            resume=self.test_file,
            current_status=ApplicationStatus.SUBMITTED
        )

        # Get all candidates ordered by created_at (default ordering)
        candidates = Candidate.objects.all()

        # The second candidate should be first in the list (most recent)
        self.assertEqual(candidates[0], second_candidate)
        self.assertEqual(candidates[1], self.candidate)


class StatusChangeModelTest(TestCase):
    """Test cases for the StatusChange model."""

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

    def test_status_change_creation(self):
        """Test that a status change can be created with valid data."""
        self.assertEqual(self.status_change.candidate, self.candidate)
        self.assertIsNone(self.status_change.previous_status)
        self.assertEqual(self.status_change.new_status, ApplicationStatus.SUBMITTED)
        self.assertEqual(self.status_change.feedback, "Application submitted successfully.")
        self.assertEqual(self.status_change.admin_user, "System")

    def test_status_change_str_representation(self):
        """Test the string representation of a status change."""
        expected_str = f"{self.candidate.full_name} - {self.status_change.new_status} - {self.status_change.created_at}"
        self.assertEqual(str(self.status_change), expected_str)

    def test_status_change_ordering(self):
        """Test that status changes are ordered by created_at in descending order."""
        # Create another status change
        second_status_change = StatusChange.objects.create(
            candidate=self.candidate,
            previous_status=ApplicationStatus.SUBMITTED,
            new_status=ApplicationStatus.UNDER_REVIEW,
            feedback="Application is under review.",
            admin_user="Admin"
        )

        # Get all status changes ordered by created_at (default ordering)
        status_changes = StatusChange.objects.all()

        # The second status change should be first in the list (most recent)
        self.assertEqual(status_changes[0], second_status_change)
        self.assertEqual(status_changes[1], self.status_change)
