import os
from django.conf import settings
from django.core.files.storage import default_storage

from opaque_keys.edx.keys import CourseKey
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.djangoapps.offline_mode.utils.assets_management import is_offline_content_present, save_asset_file
from lms.djangoapps.offline_mode.utils.xblock_helpers import is_offline_supported
from xmodule.modulestore.django import modulestore


from .file_management import save_asset_file, remove_old_files, base_storage_path
from .tasks import generate_course_media


class OfflineXBlockStatusInfoView(APIView):
    # FIXME: Add docstring

    def get(self, request, course_id):
        course_key = CourseKey.from_string(course_id)
        response_data = []

        for xblock in modulestore().get_items(course_key, qualifiers={'category': 'problem'}):
            if not is_offline_supported(xblock):
                continue
            if not is_offline_content_present(xblock):
                generate_course_media.delay(course_id)
                return Response({'status': False, 'data': []})

            base_path = base_storage_path(xblock)
            offline_zip_path = os.path.join(base_path, 'offline_content.zip')

            html_data = default_storage.url(offline_zip_path)
            if not html_data.startswith('http'):
                html_data = f'{settings.LMS_ROOT_URL}{html_data}'  # FIXME: use os.path.join

            last_modified = default_storage.get_created_time(offline_zip_path)
            size = default_storage.size(offline_zip_path)

            response_data.append({
                'link': html_data,
                'file_size': size,
                'last_modified': last_modified,
            })

        return Response({'status': True, 'data': response_data})

