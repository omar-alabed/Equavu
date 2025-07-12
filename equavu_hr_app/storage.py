"""
Storage abstraction layer for handling file storage.
This allows for easy switching between local and cloud storage solutions.
"""
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class StorageManager:
    """
    Storage manager that provides an abstraction over different storage backends.
    Currently implements local file storage, but can be extended to support
    cloud storage solutions like AWS S3, Google Cloud Storage, etc.
    TODO: Implement AWS S3 .
    """

    @staticmethod
    def get_storage():
        """
        Returns the appropriate storage backend based on configuration.
        This method can be extended to return different storage backends
        based on settings.
        """
        # Default to local file storage
        return LocalStorage()


class LocalStorage(FileSystemStorage):
    """
    Local file storage implementation.
    Extends Django's FileSystemStorage with additional functionality.
    """

    def __init__(self):
        """Initialize with media root and URL from settings."""
        super().__init__(
            location=settings.MEDIA_ROOT,
            base_url=settings.MEDIA_URL
        )

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system.
        Ensures we don't overwrite existing files.
        """
        return super().get_available_name(name, max_length)

    def path(self, name):
        """Return the full path to the file."""
        return os.path.join(settings.MEDIA_ROOT, name)

    def url(self, name):
        """Return the URL where the file can be accessed."""
        return super().url(name)


# Factory function to get the configured storage backend
def get_storage_backend():
    """Returns the configured storage backend."""
    return StorageManager.get_storage()
