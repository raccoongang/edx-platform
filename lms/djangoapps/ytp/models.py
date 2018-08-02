import os
from django.conf import settings
from django.core.urlresolvers import reverse

from django.db.models.signals import post_save
from django.dispatch import receiver

from certificates.models import GeneratedCertificate


@receiver(post_save, sender=GeneratedCertificate)
def generate_pdf(sender, instance, **kwargs):
    """
    cd /tmp
    wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.3/wkhtmltox-0.12.3_linux-generic-amd64.tar.xz
    tar xvf wkhtmltox-0.12.3_linux-generic-amd64.tar.xz
    sudo mv wkhtmltox/bin/wkhtmlto* /usr/bin/
    """
    if not instance.verify_uuid:
        return None
    pdf_filename = '{}.pdf'.format(instance.verify_uuid)
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'certs')
    pdf_url = os.path.join(settings.MEDIA_URL, 'certs', pdf_filename)

    html_cert_url = (
        'https://{}{}'.format(
            settings.SITE_NAME,
            reverse('certificates:render_cert_by_uuid', args=[instance.verify_uuid])
        )
    )

    if not os.path.exists(pdf_dir):
        os.mkdir(pdf_dir)

    cmd = '''
    xvfb-run -a --server-args="-screen 0, 1024x768x24" wkhtmltopdf --zoom 1.2887 --margin-top 5 --margin-bottom 5 \
    --margin-left 5 --margin-right 5 -s A4 -O Portrait --print-media-type {} {}
    '''
    cmd = cmd.format(html_cert_url, os.path.join(pdf_dir, pdf_filename))
    if os.path.exists(os.path.join(pdf_dir, pdf_filename)):
        os.remove(os.path.join(pdf_dir, pdf_filename))
    os.system(cmd)

    sender.objects.filter(id=instance.id).update(download_url=pdf_url)