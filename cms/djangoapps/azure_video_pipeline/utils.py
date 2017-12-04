from django.conf import settings

from .media_service import LocatorTypes, MediaServiceClient
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


def get_streaming_video_list(azure_config):
    media_service_api = get_media_service_client(azure_config)
    locators = media_service_api.get_locators_list(LocatorTypes.OnDemandOrigin)
    for locator in locators:
        files = media_service_api.get_asset_files(locator.get('AssetId'))
        yield get_streaming_video_info(files, locator)


def get_streaming_video_info(files, locator):
    filename = ''
    for vfile in files:
        if vfile.get('MimeType', '') == 'application/octet-stream' and vfile.get('Name', '').endswith('.ism'):
            filename = vfile['Name']
            break
    path = locator.get('Path').split(':', 1)[-1]
    return {
        'smooth_streaming_url': u'{}{}/manifest'.format(path, filename),
        'file_name': filename,
        'asset_id': locator.get('AssetId')
    }


def get_captions_info(locator, files):
    data = []
    path = locator.get('Path').split(':', 1)[-1]
    for cfile in files:
        if cfile.get('Name', '').endswith('.vtt'):
            filename = cfile['Name'].encode('utf-8')
            download_url = '/{}?'.format(filename).join(path.split('?'))
            data.append({
                'download_url': download_url,
                'file_name': filename,
            })
    return data


def get_captions_info_and_download_video_url(locator, files):
    captions = []
    download_video_url = ''
    file_size = 0
    path = locator.get('Path').split(':', 1)[-1]
    for afile in files:
        try:
            content_file_size = int(afile.get('ContentFileSize', 0))
        except ValueError:
            content_file_size = 0
        if afile.get('Name', '').endswith('.vtt'):
            filename = afile['Name']
            download_url = u'/{}?'.format(filename).join(path.split('?'))
            captions.append({
                'download_url': download_url,
                'file_name': filename,
            })
        elif afile.get('Name', '').endswith('.mp4') and content_file_size > file_size:
            filename = afile['Name']
            file_size = content_file_size
            download_video_url = u'/{}?'.format(filename).join(path.split('?'))

    return captions, download_video_url
