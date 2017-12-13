from django.conf import settings

from .media_service import MediaServiceClient
from .models import AzureOrgProfile


def get_azure_config(organization):
    azure_config = {}
    azure_profile = AzureOrgProfile.objects.filter(organization__short_name=organization).first()
    if azure_profile:
        azure_config = azure_profile.to_dict()
    elif all([
        settings.FEATURES.get('AZURE_CLIENT_ID'),
        settings.FEATURES.get('AZURE_CLIENT_SECRET'),
        settings.FEATURES.get('AZURE_TENANT'),
        settings.FEATURES.get('AZURE_REST_API_ENDPOINT'),
        settings.FEATURES.get('STORAGE_ACCOUNT_NAME'),
        settings.FEATURES.get('STORAGE_KEY')
    ]):
        azure_config = {
            'client_id': settings.FEATURES.get('AZURE_CLIENT_ID'),
            'secret': settings.FEATURES.get('AZURE_CLIENT_SECRET'),
            'tenant': settings.FEATURES.get('AZURE_TENANT'),
            'rest_api_endpoint': settings.FEATURES.get('AZURE_REST_API_ENDPOINT'),
            'storage_account_name': settings.FEATURES.get('STORAGE_ACCOUNT_NAME'),
            'storage_key': settings.FEATURES.get('STORAGE_KEY')
        }
    return azure_config


def get_media_service_client(organization):
    return MediaServiceClient(get_azure_config(organization))
