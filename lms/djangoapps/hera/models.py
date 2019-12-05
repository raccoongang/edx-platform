"""
Model which store and override hera onboarding pages templates and user onboarding passed states.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from mako.template import Template


def render_template(page_number):
    """
    Return rendered template as a string.
    """
    template = Template(render_to_string('hera/{}.html'.format(page_number)))
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
        return Onboarding.objects.last()

    def is_passed(self):
        """
        Checks if user pass onboarding.
        """
        if self.page_1 and self.page_2 and self.page_3 and self.page_4:
            return True
        return False

    @classmethod
    def update(cls, user, page_number):
        """
        Mark passed hera onboarding page for current user.
        page_number is the current onboarding page which user passes now.
        """
        user_onboarding, _ = cls.objects.update_or_create(user=user, defaults={page_number: True})
        return user_onboarding

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

    class Meta:
        app_label = 'hera'
