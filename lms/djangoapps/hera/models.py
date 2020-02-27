"""
Model which store and override hera onboarding pages templates and user onboarding passed states.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.template.loader import render_to_string
from mako.template import Template


CACHING_USER_ONBOARDING_TEMPLATE = 'hera:useronboarding:{user_id}'
CACHING_ONBOARDING_KEY = 'hera:onboarding'
CACHING_PAGES_KEY = 'hera:onboarding_pages'
CACHING_ACTIVE_COURSE_KEY = 'hera:active_course'
CACHING_TIMEOUT = 60 * 15


def render_template(page_number):
    """
    Return rendered template as a string.
    """
    template = Template(render_to_string('hera/{}_template.txt'.format(page_number)))
    return template.render(**{'settings': settings})


class Onboarding(models.Model):
    """
    Contain hera onboarding pages.
    """

    page_1 = models.TextField(
        blank=True,
        verbose_name='First Page',
        default=render_template('page_1')
    )
    page_2 = models.TextField(
        blank=True,
        verbose_name='Second Page',
        default=render_template('page_2')
    )
    page_3 = models.TextField(
        blank=True,
        verbose_name='Third Page',
        default=render_template('page_3')
    )
    page_4 = models.TextField(
        blank=True,
        verbose_name='Fourth Page',
        default=render_template('page_4')
    )

    @property
    def first(self):
        if not self.page_1:
            return render_template('page_1')
        return self.page_1

    @property
    def second(self):
        if not self.page_2:
            return render_template('page_2')
        return self.page_2

    @property
    def third(self):
        if not self.page_3:
            return render_template('page_3')
        return self.page_3

    @property
    def fourth(self):
        if not self.page_4:
            return render_template('page_4')
        return self.page_4

    class Meta:
        app_label = 'hera'

    def save(self, *args, **kwargs):
        super(Onboarding, self).save(*args, **kwargs)
        cache.delete(CACHING_ONBOARDING_KEY)
        cache.delete(CACHING_PAGES_KEY)


class UserOnboarding(models.Model):
    """
    Contain history of hera users onboarding states.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page_1 = models.BooleanField(default=False)
    page_2 = models.BooleanField(default=False)
    page_3 = models.BooleanField(default=False)
    page_4 = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username

    @property
    def onboarding(self):
        cached_onboarding = cache.get(CACHING_ONBOARDING_KEY)
        if cached_onboarding:
            return cached_onboarding
        onboarding = Onboarding.objects.last()
        if onboarding:
            cache.set(CACHING_ONBOARDING_KEY, onboarding, CACHING_TIMEOUT)
            return onboarding

    def is_passed(self):
        """
        Checks if user pass onboarding.
        """
        if self.page_1 and self.page_2 and self.page_3 and self.page_4:
            return True
        return False

    @staticmethod
    def get_cache(user_id):
        return cache.get(
            CACHING_USER_ONBOARDING_TEMPLATE.format(user_id=user_id)
        )

    @staticmethod
    def set_cache(user_id):
        cache.set(
            CACHING_USER_ONBOARDING_TEMPLATE.format(user_id=user_id),
            True,
            CACHING_TIMEOUT
        )

    @staticmethod
    def delete_cache(user_id):
        cache.delete(
            CACHING_USER_ONBOARDING_TEMPLATE.format(user_id=user_id)
        )

    @classmethod
    def onboarding_is_passed(cls, user_id):
        if cls.get_cache(user_id):
            return True
        else:
            user_onboarding = cls.objects.filter(user_id=user_id).first()
            if user_onboarding and user_onboarding.is_passed():
                cls.set_cache(user_id)
                return True
            return False
        return False

    @classmethod
    def update(cls, user, page_number):
        """
        Mark passed hera onboarding page for current user.
        page_number is the current onboarding page which user passes now.
        """
        user_onboarding, _ = cls.objects.update_or_create(user=user, defaults={page_number: True})
        if user_onboarding.is_passed():
            cls.set_cache(user.id)
        return user_onboarding

    def save(self, *args, **kwargs):
        super(UserOnboarding, self).save(*args, **kwargs)
        self.__class__.delete_cache(self.user_id)

    def delete(self, *args, **kwargs):
        super(UserOnboarding, self).delete(*args, **kwargs)
        self.__class__.delete_cache(self.user_id)


    def get_last_passed(self):
        """
        Return last passed user page.
        """
        for _, num in enumerate(reversed(range(1, 5))):
            field_name = 'page_{}'.format(num)
            if getattr(self, field_name):
                return field_name

    def get_current_page(self):
        """
        Return current page for current user.
        """
        for num, _ in enumerate(range(4), 1):
            field_name = 'page_{}'.format(num)
            if not getattr(self, field_name):
                return field_name
        return 'page_1'

    def are_all_passed(self):
        return all([
            getattr(self, 'page_{}'.format(ind)) for ind, _ in enumerate(range(4), 1)
        ])

    def get_next_page(self, current=None):
        """
        Return next page for current user.
        """
        if current:
            page_number = int(current.split('_')[-1])
            if page_number < 4:
                return 'page_{}'.format(page_number+1)
            else:
                return 'page_1'
        if self.get_last_passed():
            last_passed_number = int(self.get_last_passed().split('_')[-1])
            if last_passed_number < 4:
                return 'page_{}'.format(last_passed_number+1)
        return 'page_1'

    def get_pages(self):
        """
        Return content of hera onboarding pages.
        """
        return [
            {
                'content': self.onboarding.first if self.onboarding else render_template('page_1'),
                'passed': self.page_1,
                'name': 'page_1'
            },
            {
                'content': self.onboarding.second if self.onboarding else render_template('page_2'),
                'passed': self.page_2,
                'name': 'page_2'
            },
            {
                'content': self.onboarding.third if self.onboarding else render_template('page_3'),
                'passed': self.page_3,
                'name': 'page_3'
            },
            {
                'content': self.onboarding.fourth if self.onboarding else render_template('page_4'),
                'passed': self.page_4,
                'name': 'page_4'
            }
        ]

    @staticmethod
    def get_static_pages():
        cached_pages = cache.get(CACHING_PAGES_KEY)
        if cached_pages:
            return cached_pages
        onboarding = Onboarding.objects.last()
        pages = [
            {
                'content': onboarding.first if onboarding else render_template('page_1'),
            },
            {
                'content': onboarding.second if onboarding else render_template('page_2'),
            },
            {
                'content': onboarding.third if onboarding else render_template('page_3'),
            },
            {
                'content': onboarding.fourth if onboarding else render_template('page_4'),
            }
        ]
        cache.set(CACHING_PAGES_KEY, pages, CACHING_TIMEOUT)
        return pages

    class Meta:
        app_label = 'hera'


class ActiveCourseSetting(models.Model):
    course = models.ForeignKey("course_overviews.CourseOverview", on_delete=models.CASCADE)


    def __unicode__(self):
        return unicode(self.course.id)

    @classmethod
    def get(cls):
        """
        Returns a cached active course if is.
        """
        cached_course = cache.get(CACHING_ACTIVE_COURSE_KEY)
        if cached_course:
            return cached_course
        else:
            last = cls.objects.last()
            if last:
                last_course_id = last.course.id
                cache.set(CACHING_ACTIVE_COURSE_KEY, last_course_id, CACHING_TIMEOUT)
                return last_course_id

    def save(self, *args, **kwargs):
        super(ActiveCourseSetting, self).save(*args, **kwargs)
        cache.delete(CACHING_ACTIVE_COURSE_KEY)

    def delete(self, *args, **kwargs):
        super(ActiveCourseSetting, self).delete(*args, **kwargs)
        cache.delete(CACHING_ACTIVE_COURSE_KEY)


class Mascot(models.Model):
    user_dashboard = models.ImageField(upload_to='hera', null=True, blank=True)
    user_dashboard_modal = models.ImageField(upload_to='hera', null=True, blank=True)
    onboarding = models.ImageField(upload_to='hera', null=True, blank=True)

    @classmethod
    def _instance(cls):
        return cls.objects.first()

    @classmethod
    def onboarding_img_url(cls):
        instance = cls._instance()
        if instance:
            return instance.onboarding.url if instance.onboarding else None

    @classmethod
    def user_dashboard_img_urls(cls):
        instance = cls._instance()
        if instance:
            user_dashboard = instance.user_dashboard.url if instance.user_dashboard else None
            user_dashboard_modal = instance.user_dashboard_modal.url if instance.user_dashboard_modal else None
            return {
                'user_dashboard': user_dashboard,
                'user_dashboard_modal': user_dashboard_modal
            }
        return {}


@receiver(post_delete, sender=ActiveCourseSetting)
def reset_active_course(sender, instance, *args, **kwargs):
    """
    Reset cache for ActiveCourseSetting.
    The signal is used due to the fact that when deleting from the admin
    using action 'delete_selected', 'Model.delete' is not called.
    """
    cache.delete(CACHING_ACTIVE_COURSE_KEY)


@receiver(post_delete, sender=UserOnboarding)
def reset_user_onboarding(sender, instance, *args, **kwargs):
    """
    Reset cache for UserOnboarding.
    The signal is used due to the fact that when deleting from the admin
    using action 'delete_selected', 'Model.delete' is not called.
    """
    cache.delete(
        CACHING_USER_ONBOARDING_TEMPLATE.format(user_id=instance.user_id, model_name=sender.__name__)
    )
