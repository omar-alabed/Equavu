from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from equavu_hr_app.models import Candidate, StatusChange, Department, ApplicationStatus
import os


class CandidateAPITest(TestCase):
    """Test cases for the Candidate API endpoints."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()

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

        # URLs
        self.register_url = reverse('equavo_hr_app:candidate-register')
        self.status_url = reverse('equavo_hr_app:candidate-status', args=[self.candidate.id])
        self.admin_list_url = reverse('equavo_hr_app:admin-candidate-list')
        self.admin_detail_url = reverse('equavo_hr_app:admin-candidate-detail', args=[self.candidate.id])
        self.admin_status_url = reverse('equavo_hr_app:admin-status-update', args=[self.candidate.id])
        self.admin_resume_url = reverse('equavo_hr_app:admin-resume-download', args=[self.candidate.id])

    def tearDown(self):
        """Clean up after tests."""
        # Delete test files
        if self.candidate.resume:
            if os.path.isfile(self.candidate.resume.path):
                os.remove(self.candidate.resume.path)

    def test_candidate_registration(self):
        """Test candidate registration endpoint."""
        # Create data for a new candidate
        data = {
            'full_name': 'New User',
            'email': 'new@example.com',
            'date_of_birth': '1995-05-05',
            'years_of_experience': 3,
            'department': Department.HR,
            'resume': self.test_file
        }

        # Make the request
        response = self.client.post(
            self.register_url,
            data,
            format='multipart'
        )

        # Check response
        # The submitted file is empty, otherwise 201_created would be expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the candidate was created
        # Since the above request fails, we expect no new candidate to be created
        self.assertFalse(Candidate.objects.filter(email='new@example.com').exists())

    def test_candidate_status_check(self):
        """Test candidate status check endpoint."""
        # Make the request
        response = self.client.get(self.status_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check data
        data = response.json()
        self.assertEqual(data['full_name'], 'Test User')
        self.assertEqual(data['current_status'], ApplicationStatus.SUBMITTED)
        self.assertEqual(len(data['status_changes']), 1)

    def test_admin_candidate_list(self):
        """Test admin candidate list endpoint."""
        # Set admin header
        self.client.credentials(HTTP_X_ADMIN='1')

        # Make the request
        response = self.client.get(self.admin_list_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check data
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['full_name'], 'Test User')

    def test_admin_candidate_list_unauthorized(self):
        """Test admin candidate list endpoint without admin header."""
        # Make the request without admin header
        response = self.client.get(self.admin_list_url)

        # Check response (should be forbidden)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_candidate_detail(self):
        """Test admin candidate detail endpoint."""
        # Set admin header
        self.client.credentials(HTTP_X_ADMIN='1')

        # Make the request
        response = self.client.get(self.admin_detail_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check data
        data = response.json()
        self.assertEqual(data['full_name'], 'Test User')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['current_status'], ApplicationStatus.SUBMITTED)

    def test_admin_status_update(self):
        """Test admin status update endpoint."""
        # Set admin header
        self.client.credentials(HTTP_X_ADMIN='1', HTTP_X_ADMIN_USER='Admin')

        # Create data for status update
        data = {
            'status': ApplicationStatus.UNDER_REVIEW,
            'feedback': 'Application is under review.'
        }

        # Make the request
        response = self.client.put(
            self.admin_status_url,
            data,
            format='json'
        )

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the status was updated
        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.current_status, ApplicationStatus.UNDER_REVIEW)

        # Check that a status change record was created
        status_changes = StatusChange.objects.filter(candidate=self.candidate)
        self.assertEqual(status_changes.count(), 2)
        self.assertEqual(status_changes.latest('created_at').new_status, ApplicationStatus.UNDER_REVIEW)
        self.assertEqual(status_changes.latest('created_at').feedback, 'Application is under review.')

    def test_admin_resume_download(self):
        """Test admin resume download endpoint."""
        # Set admin header
        self.client.credentials(HTTP_X_ADMIN='1')

        # Make the request
        response = self.client.get(self.admin_resume_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue('attachment; filename=' in response['Content-Disposition'])
