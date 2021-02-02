"""
Partners models.
"""
import os
import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from model_utils.models import TimeStampedModel

ALLOWED_IMG_FORMATS = (
    ".png",
    ".svg",
    ".jpeg",
    ".jpg",
)
PARTNERS_ASSETS_DIRNAME = "partners_assets"


def partners_assets_path(_, filename):
    """
    Delete the file if it already exist and returns the partner logo asset file path.

    Arguments:
        _ (`Partner` obj): partner instance.
        filename (str): asset filename e.g. "filename.png".

    Returns:
        asset path (str): path of asset file e.g. partners_assets/filename_1269884900.png
    """
    file_name, file_extension = os.path.splitext(filename)
    # Sign with timestamp to avoid duplicates
    file_name += str(int(time.time()))
    name = os.path.join(
        PARTNERS_ASSETS_DIRNAME,
        file_name + file_extension,
    )
    fullname = os.path.join(settings.MEDIA_ROOT, name)
    # There can still be duplicates. Partners logos can get messed up
    if os.path.exists(fullname):
        os.remove(fullname)
    return name


def validate_partner_image(image):
    """
    Validates that a particular image is small enough and is of allowed format.

    Format check solely relies on extension.
    NOTE: wait for Django 1.11+ to use `validate_image_file_extension`.
    """
    _, file_extension = os.path.splitext(image.name)
    if file_extension not in ALLOWED_IMG_FORMATS:
        raise ValidationError(
            "Allowed file formats: {!s}".format(" ".join(ALLOWED_IMG_FORMATS))
        )


class Partner(TimeStampedModel):
    """
    Store partners information including partners assets e.g. logos.
    """

    name = models.CharField(
        max_length=255,
        help_text="Partner organization title.",
    )
    url = models.CharField(
        max_length=255,
        help_text="Partner website url.",
    )
    # ImageField doesn't support SVG
    image = models.FileField(
        upload_to=partners_assets_path,
        validators=[validate_partner_image],
        help_text="Partner logo image.",
    )
