"""
Utility functions for edx-ace.
"""
import logging

log = logging.getLogger(__name__)


def setup_firebase_app(firebase_credentials, app_name='fcm-app'):
    """
    Returns a Firebase app instance if the Firebase credentials are provided.
    """
    try:
        import firebase_admin  # pylint: disable=import-outside-toplevel
    except ImportError:
        log.error('Could not import firebase_admin package.')
        return
    if firebase_credentials:
        certificate = firebase_admin.credentials.Certificate(firebase_credentials)
        return firebase_admin.initialize_app(certificate, name=app_name)
