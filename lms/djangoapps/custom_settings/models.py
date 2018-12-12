"""
Database models for the custom settings app
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _


class HomepageVideo(models.Model):
    """
    Contains a video link for the homepage.
    """
    link = models.URLField(
        max_length=255,
        help_text=_(
            "Add or edit link for the video. <b>Important</b>: insert only a link, without iframe width, height, "
            "frameborder or any other attributes. Click <a href='https://support.google.com/youtube/answer/171780'>"
            "here</a> to see how to embed Youtube video or playlist. "
            "Click <a href='https://help.vimeo.com/hc/en-us/articles/360000710167-Accessing-and-editing-embed-codes'>"
            "here</a> to see how to embed Vimeo video. Your link should be playable directly from the browser. "
            "<b>Example:</b> https://www.youtube.com/embed/videoseries?list=PLx0sYbCqOb8TBPRdmBHs5Iftvv9TPboYG."
        )
    )

    def __unicode__(self):
        return _(u"Homepage video link is {link}").format(link=self.link)


class HomepageSlider(models.Model):
    """
    Contains a slider's content for the homepage.
    """
    title = models.CharField(max_length=255)
    image = models.ImageField(
        help_text=_("Size of images must be at least 800 pixels horizontally and 450 pixels vertically and all images must be the same size")
    )
    description = models.TextField()
    link = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("If you want to add an URL to your message, paste it here.")
    )
    is_published = models.BooleanField(
        default=False,
        help_text=_(
            "Set this value to True if you want this slide to be shown on Homepage"
        )
    )
    slide_order = models.PositiveIntegerField(
        help_text=_(
            "Use integers to set an order of appearance for your slides. 1 goes first."
        )
    )

    class Meta(object):
        ordering = ['slide_order']

    def __unicode__(self):
        return _(u"Slide Title: {title}, Order: {slide_order}").format(
            slide_order=self.slide_order,
            title=self.title
        )
