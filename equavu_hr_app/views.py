from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework import status, permissions, generics, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from .models import Candidate, StatusChange, ApplicationStatus
from .serializers import (
    CandidateListSerializer,
    CandidateDetailSerializer,
    CandidateCreateSerializer,
    StatusUpdateSerializer
)
# from .storage import get_storage_backend
import logging
import os

logger = logging.getLogger(__name__)


# Simple API view for testing
class APITestView(APIView):
    """
    A simple API view for testing API routing.
    """
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        """
        Return a simple JSON response to test API routing.
        """
        return Response({
            'status': 'success',
            'message': 'API is working properly',
            'endpoints': {
                'candidates_register': '/api/candidates/register/',
                'candidate_status': '/api/candidates/{candidate_id}/status/',
                'admin_candidates': '/api/admin/candidates/',
            }
        })


# Custom permission class for admin authentication
class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    Admin users are identified by the X-ADMIN header.
    """
    def has_permission(self, request, view):
        return request.headers.get('X-ADMIN') == '1'


# Candidate Registration View
class CandidateRegistrationView(generics.CreateAPIView):
    """
    API endpoint for candidate registration.
    Allows candidates to register with their information and upload a resume.
    """
    serializer_class = CandidateCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        logger.info(f"New candidate registration: {serializer.validated_data.get('full_name')}")
        candidate = serializer.save(current_status=ApplicationStatus.SUBMITTED)

        # Create initial status change record
        StatusChange.objects.create(
            candidate=candidate,
            previous_status=None,
            new_status=ApplicationStatus.SUBMITTED,
            feedback="Application submitted successfully."
        )

        return candidate


# Candidate Status View
class CandidateStatusView(generics.RetrieveAPIView):
    """
    API endpoint for candidates to check their application status.
    """
    serializer_class = CandidateDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        candidate_id = self.kwargs.get('pk')
        return get_object_or_404(Candidate, id=candidate_id)


# Admin Candidate List View
class CandidateListView(generics.ListAPIView):
    """
    API endpoint for admins to list all candidates.
    Supports filtering by department and pagination.
    """
    serializer_class = CandidateListSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']  # Default ordering by registration date (descending)

    def get_queryset(self):
        queryset = Candidate.objects.all()

        # Filter by department if provided
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department=department)

        return queryset


# Admin Candidate Detail View
class CandidateDetailView(generics.RetrieveAPIView):
    """
    API endpoint for admins to view candidate details.
    """
    serializer_class = CandidateDetailSerializer
    permission_classes = [IsAdmin]

    def get_object(self):
        candidate_id = self.kwargs.get('pk')
        return get_object_or_404(Candidate, id=candidate_id)


# Admin Status Update View
class StatusUpdateView(generics.UpdateAPIView):
    """
    API endpoint for admins to update a candidate's application status.
    """
    serializer_class = StatusUpdateSerializer
    permission_classes = [IsAdmin]

    def get_object(self):
        candidate_id = self.kwargs.get('pk')
        return get_object_or_404(Candidate, id=candidate_id)

    def update(self, request, *args, **kwargs):
        candidate = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            feedback = serializer.validated_data.get('feedback', '')
            admin_user = request.headers.get('X-ADMIN-USER', 'Admin')

            # Create status change record
            StatusChange.objects.create(
                candidate=candidate,
                previous_status=candidate.current_status,
                new_status=new_status,
                feedback=feedback,
                admin_user=admin_user
            )

            # Update candidate status
            candidate.current_status = new_status
            candidate.save()

            logger.info(f"Status updated for candidate {candidate.id}: {new_status}")

            # Return updated candidate details
            return Response({
                'message': 'Status updated successfully',
                'candidate': CandidateDetailSerializer(candidate).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Resume Download View
class ResumeDownloadView(generics.GenericAPIView):
    """
    API endpoint for admins to download a candidate's resume.
    """
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        candidate = get_object_or_404(Candidate, id=pk)

        if not candidate.resume:
            return Response(
                {'error': 'Resume not found for this candidate'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # storage = get_storage_backend()
            file_path = candidate.resume.path

            if not os.path.exists(file_path):
                return Response(
                    {'error': 'Resume file not found on storage'},
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.info(f"Resume downloaded for candidate {candidate.id}")

            # Get file name from path
            file_name = os.path.basename(candidate.resume.name)

            # Determine content type based on file extension
            content_type = 'application/pdf' if file_name.endswith('.pdf')\
                else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

            # Return file response
            response = FileResponse(open(file_path, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response

        except Exception as e:
            logger.error(f"Error downloading resume for candidate {candidate.id}: {str(e)}")
            return Response(
                {'error': 'Error downloading resume'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
