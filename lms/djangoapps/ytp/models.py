import os
from django.conf import settings
from django.core.urlresolvers import reverse

from django.db.models.signals import post_save
from django.dispatch import receiver

from certificates.models import GeneratedCertificate
from openedx.core.djangoapps.site_configuration.helpers import get_value_for_org

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

    site_domain = get_value_for_org(instance.course_id.org, 'site_domain')
    if not site_domain:
        site_domain = settings.SITE_NAME

    html_cert_url = (
        'https://{}{}'.format(
            site_domain,
            reverse('certificates:render_cert_by_uuid', args=[instance.verify_uuid])
        )
    )

    if not os.path.exists(pdf_dir):
        os.mkdir(pdf_dir)

    cmd = '''
    xvfb-run -a --server-args="-screen 0, 1024x768x24" wkhtmltopdf  --margin-top 1 --margin-bottom 0 \
    --margin-left 1 --margin-right 1 -s A4 -O Landscape --print-media-type  --run-script '{}' {} {}
    '''
    script = '''
    var x = document.getElementsByClassName("certificates"); 
    var i; 
    for (i = 0; i < x.length; i++) {
      x[i].style.maxHeight = "100% !important";
      x[i].style.maxWidth = "100% !important"; 
      x[i].style.height = "768px !important"; 
    }
    '''
    cmd = cmd.format(script, html_cert_url, os.path.join(pdf_dir, pdf_filename))
    if os.path.exists(os.path.join(pdf_dir, pdf_filename)):
        os.remove(os.path.join(pdf_dir, pdf_filename))
    os.system(cmd)

    sender.objects.filter(id=instance.id).update(download_url=pdf_url)
