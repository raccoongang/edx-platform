"""
Custom PDF certificates logic.
"""
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from edxmako.shortcuts import render_to_string
from xhtml2pdf import pisa


@login_required
def download_certificate_pdf(request):
    """
    Handle a request to download a certificate in the pdf form.
    """
    # TODO remove social sharing from the for-pdf template
    template_rel_path = "certificates/valid_pdf.html"  # "certificates/valid.html"

    # TODO provide context with the request
    context_dict = {
        'accomplishment_banner_congrats': u'\u041f\u043e\u0437\u0434\u0440\u0430\u0432\u043b\u044f\u0435\u043c!  \u042d\u0442\u0430 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430 \u0441\u043e\u0434\u0435\u0440\u0436\u0438\u0442 \u0432\u0441\u0435 \u0432\u0430\u0448\u0438 \u0434\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u044f.  \u041f\u043e\u0434\u0435\u043b\u0438\u0442\u0435\u0441\u044c \u0435\u044e \u0441 \u0441\u0435\u043c\u044c\u0451\u0439, \u0434\u0440\u0443\u0437\u044c\u044f\u043c\u0438 \u0438 \u043a\u043e\u043b\u043b\u0435\u0433\u0430\u043c\u0438 \u0432 \u0441\u0432\u043e\u0438\u0445 \u0441\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0445 \u0438 \u043f\u0440\u043e\u0444\u0435\u0441\u0441\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0445 \u0441\u0435\u0442\u044f\u0445.',
        'accomplishment_copy_description_full': u'\u0443\u0441\u043f\u0435\u0448\u043d\u043e \u0437\u0430\u0432\u0435\u0440\u0448\u0438\u043b, \u043f\u043e\u043b\u0443\u0447\u0438\u043b \u043f\u0440\u043e\u0445\u043e\u0434\u043d\u043e\u0439 \u0431\u0430\u043b\u043b, \u0438 \u0431\u044b\u043b \u0443\u0434\u043e\u0441\u0442\u043e\u0435\u043d \u0421\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u0430  Verified \u043e\u0431 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u0438 \u043a\u0443\u0440\u0441\u0430 \u043d\u0430 Your Platform Name Here',
        'badge': None,
        'eng_cert_course_name': u'',
        'accomplishment_copy_course_description': u'\u043a\u0443\u0440\u0441 \u043f\u0440\u0435\u0434\u043e\u0441\u0442\u0430\u0432\u043b\u0435\u043d MAMA.',
        'accomplishment_copy_name': u'Olena Persianova',
        'points_earned': 1.0,
        'share_url': 'http://0.0.0.0:9300/certificates/bb238da30c10487ca741572f856f1d74',
        'course_mode': u'verified',
        'accomplishment_banner_opening': u'Olena Persianova, \u0432\u044b \u043f\u043e\u043b\u0443\u0447\u0438\u043b\u0438 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442!',
        u'accomplishment_class_append': u'accomplishment-certificate',
        'accomplishment_copy_more_about': u'\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u0434\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u044f\u0445 \u0441\u043b\u0443\u0448\u0430\u0442\u0435\u043b\u044f Olena Persianova',
        'company_about_title': u'\u041e \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u0435 Your Platform Name Here',
        'company_contact_urltext': u'\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b Your Platform Name Here',
        'facebook_share_text': u'\u041c\u043d\u043e\u0439 \u043f\u0440\u043e\u0439\u0434\u0435\u043d \u043a\u0443\u0440\u0441 \xabMAMA Course Title\xbb \u0432 Your Platform Name Here.',
        'facebook_app_id': u'FACEBOOK_APP_ID',
        'course_id': u'course-v1:MAMA+MAMA101+2020_MAMA01',
        'organization_short_name': u'MAMA',
        'company_about_urltext': u'\u0423\u0437\u043d\u0430\u0439 \u0431\u043e\u043b\u044c\u0448\u0435 \u043e Your Platform Name Here',
        'certificate_verify_title': u'\u041a\u0430\u043a Your Platform Name Here \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0435\u0442 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u044b \u043e\u0431 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u0438',
        'full_course_image_url': 'http://0.0.0.0:9300/asset-v1:MAMA+MAMA101+2020_MAMA01+type@asset+block@images_course_image.jpg',
        'company_careers_urltext': u'\u0412\u0430\u043a\u0430\u043d\u0441\u0438\u0438 Your Platform Name Here',
        'accomplishment_copy_course_org': u'MAMA',
        'company_tos_urltext': u'\u0423\u0441\u043b\u043e\u0432\u0438\u044f \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u0438\u044f \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u044b',
        'certificate_type_description': u'Verified \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442 \u043e\u0437\u043d\u0430\u0447\u0430\u0435\u0442, \u0447\u0442\u043e \u0441\u043b\u0443\u0448\u0430\u0442\u0435\u043b\u044c \u043e\u0431\u044f\u0437\u0430\u043b\u0441\u044f \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u0442\u044c \u041a\u043e\u0434\u0435\u043a\u0441 \u0447\u0435\u0441\u0442\u0438 Your Platform Name Here \u0438 \u0437\u0430\u0432\u0435\u0440\u0448\u0438\u043b \u0432\u0441\u0435 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u044b\u0435 \u0437\u0430\u0434\u0430\u043d\u0438\u044f \u0434\u0430\u043d\u043d\u043e\u0433\u043e \u043a\u0443\u0440\u0441\u0430 \u0432 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0438\u0438 \u0441 \u0435\u0433\u043e \u0440\u0443\u043a\u043e\u0432\u043e\u0434\u044f\u0449\u0438\u043c\u0438 \u043f\u0440\u0438\u043d\u0446\u0438\u043f\u0430\u043c\u0438. Verified \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442 \u0442\u0430\u043a\u0436\u0435 \u0443\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442 \u043d\u0430 \u0442\u043e, \u0447\u0442\u043e \u043b\u0438\u0447\u043d\u043e\u0441\u0442\u044c \u0441\u043b\u0443\u0448\u0430\u0442\u0435\u043b\u044f \u043f\u0440\u043e\u0432\u0435\u0440\u0435\u043d\u0430 \u0438 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430.', u'logo_src': '/static/edx-theme/images/logo.png', 'company_courselist_urltext': u'\u0423\u0447\u0438\u0442\u0435\u0441\u044c \u0441 Your Platform Name Here',
        u'certificate_type': u'Verified',
        'company_about_description': u'Your Platform Name Here \u043f\u0440\u0435\u0434\u043e\u0441\u0442\u0430\u0432\u043b\u044f\u0435\u0442 \u0438\u043d\u0442\u0435\u0440\u0430\u043a\u0442\u0438\u0432\u043d\u044b\u0435 \u043e\u043d\u043b\u0430\u0439\u043d-\u043a\u0443\u0440\u0441\u044b.',
        'certificate_verify_urltext': u'\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u0435 \u044d\u0442\u043e\u0442 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442 \u0441\u0430\u043c\u043e\u0441\u0442\u043e\u044f\u0442\u0435\u043b\u044c\u043d\u043e',
        'course_number': u'MAMA101',
        'copyright_text': u'&copy; 2020 Your Platform Name Here. \u0412\u0441\u0435 \u043f\u0440\u0430\u0432\u0430 \u0437\u0430\u0449\u0438\u0449\u0435\u043d\u044b.',
        'logo_subtitle': u'\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u0430',
        u'logo_url': 'http://localhost:8000',
        'accomplishment_copy_about': u'\u041e \u0434\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u044f\u0445 \u043d\u0430 Your Platform Name Here',
        'course_end_date': u'01 \u044f\u043d\u0432\u0430\u0440\u044f 2030',
        'certificate_verify_description': u'\u0421\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u044b, \u0432\u044b\u0434\u0430\u043d\u043d\u044b\u0435 Your Platform Name Here, \u043f\u043e\u0434\u043f\u0438\u0441\u044b\u0432\u0430\u044e\u0442\u0441\u044f gpg-\u043a\u043b\u044e\u0447\u043e\u043c, \u0442\u0430\u043a \u0447\u0442\u043e \u043e\u043d\u0438 \u043c\u043e\u0433\u0443\u0442 \u0431\u044b\u0442\u044c \u043f\u0440\u043e\u0432\u0435\u0440\u0435\u043d\u044b \u0441\u0430\u043c\u043e\u0441\u0442\u043e\u044f\u0442\u0435\u043b\u044c\u043d\u043e \u0441 \u043f\u043e\u043c\u043e\u0449\u044c\u044e \u043e\u0442\u043a\u0440\u044b\u0442\u043e\u0433\u043e \u043a\u043b\u044e\u0447\u0430 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u044b \xabYour Platform Name Here\xbb. \u0414\u043b\u044f \u043d\u0435\u0437\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0439 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438, Your Platform Name Here \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442 \u0442\u0430\u043a \u043d\u0430\u0437\u044b\u0432\u0430\u0435\u043c\u0443\u044e "\u043e\u0442\u0434\u0435\u043b\u0451\u043d\u043d\u0443\u044e \u043f\u043e\u0434\u043f\u0438\u0441\u044c"&quot;".',
        'username': u'opersian',
        'document_meta_description': u'\u042d\u0442\u043e \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442 Your Platform Name Here \u0434\u043b\u044f Olena Persianova, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 \u043f\u0440\u0438\u043d\u0438\u043c\u0430\u043b \u0443\u0447\u0430\u0441\u0442\u0438\u0435 \u0432 MAMA MAMA101',
        'certificate_info_description': u'Your Platform Name Here \u043f\u0440\u0438\u0437\u043d\u0430\u0451\u0442 \u0434\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u044f \u043f\u043e\u0441\u0440\u0435\u0434\u0441\u0442\u0432\u043e\u043c \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0432, \u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u043f\u0440\u0438\u0441\u0443\u0436\u0434\u0430\u044e\u0442\u0441\u044f \u0437\u0430 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u0443\u0447\u0435\u0431\u043d\u044b\u0445 \u0437\u0430\u0434\u0430\u043d\u0438\u0439 \u043a\u0443\u0440\u0441\u0430 Your Platform Name Here.',
        'linked_in_url': None,
        'certificate_id_number_title': u'\u041d\u043e\u043c\u0435\u0440 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u0430',
        'twitter_url': '',
        u'company_privacy_url': u'/privacy',
        'document_banner': u'Your Platform Name Here \u043f\u0440\u0438\u0437\u043d\u0430\u0451\u0442 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0435 \u0434\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u044f \u043e\u0431\u0443\u0447\u0430\u044e\u0449\u0435\u0433\u043e\u0441\u044f',
        'organization_logo': None,
        'certificate_date_issued_title': u'\u0412\u044b\u0434\u0430\u043d:',
        'accomplishment_copy_course_name': u'MAMA Course Title',
        'twitter_share_text': u'\u042f \u043e\u043a\u043e\u043d\u0447\u0438\u043b \u043a\u0443\u0440\u0441 \u043d\u0430 Your Platform Name Here. \u0412\u0437\u0433\u043b\u044f\u043d\u0438\u0442\u0435 \u043d\u0430 \u043c\u043e\u0439 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442!',
        'grade_percentage': 100,
        'organization_long_name': None,
        'facebook_share_enabled': False,
        'accomplishment_copy_username': u'opersian',
        'certificate_date_issued': u'21 \u0434\u0435\u043a\u0430\u0431\u0440\u044f 2020',
        'certificate_data': {
            u'course_title': u'MAMA Course Title',
            u'name': u'Name of the certificate',
            u'is_active': True,
            u'signatories': [
                {u'name': u'', u'certificate': None, u'title': u'', u'organization': u'', u'signature_image_path': u'', u'id': 914579627}],
                u'version': 1, u'editing': False, u'id': 858626688, u'description': u'Description of the certificate'
        },
        'document_title': u'\u0421\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442 MAMA MAMA101 | Your Platform Name Here', u'company_tos_url': u'/honor',
        'accomplishment_user_id': 6L, u'company_verified_certificate_url': u'http://www.example.com/verified-certificate',
        'company_privacy_urltext': u'\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0430 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438', 'certificate_info_title': u'\u041e \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u0430\u0445 Your Platform Name Here', 'certificate_verify_url': 'Nonebb238da30c10487ca741572f856f1d74None', 'accomplishment_more_title': u'\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u0435 \u0441\u043b\u0443\u0448\u0430\u0442\u0435\u043b\u044f\n Olena Persianova:', 'certificate_id_number': u'bb238da30c10487ca741572f856f1d74', 'platform_name': u'Your Platform Name Here', 'twitter_share_enabled': False, u'certificate_title': u'Verified Certificate of Achievement', u'company_about_url': u'/about', 'points_total': 1.0}

    html = render_to_string(template_rel_path, context_dict)
    result = BytesIO()
    #pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    # TODO styles
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)  # FIXME ru, rn

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
