from django.db import models
from django.conf import settings
from hvad.models import TranslatableModel, TranslatedFields


def get_pages():
    pages = (
        ('theme-blog.html', 'blog'),
        ('theme-contact.html', 'contact'),
        ('theme-donate.html', 'donate'),
        ('theme-faq.html', 'faq'),
        ('theme-help.html', 'help'),
        ('theme-jobs.html', 'jobs'),
        ('theme-news.html', 'news'),
        ('theme-press.html', 'press'),
        ('theme-media-kit.html', 'media-kit')
    )

    for key, value in settings.MKTG_URL_LINK_MAP.items():
        if value is None or key == "ROOT" or key == "COURSES":
            continue

        template = "%s.html" % key.lower()

        if settings.FEATURES.get("USE_CUSTOM_THEME"):
            template = "theme-" + template

        pages += ((template, value),)

    return pages


class InfoPage(TranslatableModel):
    PAGES = get_pages()

    page = models.CharField(max_length=50, choices=PAGES)
    translations = TranslatedFields(
        title = models.CharField(max_length=255),
        text = models.TextField()
    )

    def __unicode__(self):
        return self.page
