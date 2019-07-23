"""
This file contains celery tasks for sending email
"""
import logging

from boto.exception import NoAuthHandlerFound
from celery.exceptions import MaxRetriesExceededError
from celery.task import task  # pylint: disable=no-name-in-module, import-error
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.template.loader import render_to_string

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

from tedix_ro.utils import get_payment_link

log = logging.getLogger('edx.celery.task')


@task
def send_payment_link_to_parent(user_id):
    """
    Sending an payment link email to the parent.
    """
    ParentProfile = apps.get_model('tedix_ro', 'ParentProfile')
    try:
        user = User.objects.get(pk=user_id)
        parent = user.parentprofile
        from_address = configuration_helpers.get_value(
            'email_from_address',
            settings.DEFAULT_FROM_EMAIL
        )
        context = {
            'payment_link': get_payment_link(user),
            'lms_url': configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
            'platform_name': configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME),
            'support_url': configuration_helpers.get_value('SUPPORT_SITE_LINK', settings.SUPPORT_SITE_LINK),
            'support_email': configuration_helpers.get_value('CONTACT_EMAIL', settings.CONTACT_EMAIL),
        }

        if user.is_active and parent:
            for student in parent.students.filter(paid=False, user__is_active=True):
                message = render_to_string('emails/payment_link_email_parent.txt', context)
                subject = 'Plata abonament TEDIX'
                mail.send_mail(
                        subject,
                        message,
                        from_address,
                        [user.email]
                    )
                log.info("send_payment_link_to_parent: Email has been sent to User {user_email}".format(
                    user_email=user.email
                ))
    except ParentProfile.DoesNotExist:
        log.error("send_payment_link_to_parent: This user has no parentprofile.")
    except User.DoesNotExist:
        log.error("send_payment_link_to_parent: User with this ID does not exist.")


@task(bind=True)
def send_activation_email(self, subject, message, from_address, dest_addr):
    """
    Sending an activation email to the user.
    """
    max_retries = settings.RETRY_ACTIVATION_EMAIL_MAX_ATTEMPTS
    retries = self.request.retries
    try:
        mail.send_mail(subject, message, from_address, [dest_addr], fail_silently=False)
        # Log that the Activation Email has been sent to user without an exception
        log.info("Activation Email has been sent to User {user_email}".format(
            user_email=dest_addr
        ))
    except NoAuthHandlerFound:  # pylint: disable=broad-except
        log.info('Retrying sending email to user {dest_addr}, attempt # {attempt} of {max_attempts}'. format(
            dest_addr=dest_addr,
            attempt=retries,
            max_attempts=max_retries
        ))
        try:
            self.retry(countdown=settings.RETRY_ACTIVATION_EMAIL_TIMEOUT, max_retries=max_retries)
        except MaxRetriesExceededError:
            log.error(
                'Unable to send activation email to user from "%s" to "%s"',
                from_address,
                dest_addr,
                exc_info=True
            )
    except Exception:  # pylint: disable=bare-except
        log.exception(
            'Unable to send activation email to user from "%s" to "%s"',
            from_address,
            dest_addr,
            exc_info=True
        )
        raise Exception
