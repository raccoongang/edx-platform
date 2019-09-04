"""
Model which store and override onboarding pages templates and user onboarding passed states.
"""
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string


def get_template(page_number):
    """
    Method which return path to default onboarding templates.
    """
    return 'onboarding/{}.html'.format(page_number)


class Onboarding(models.Model):
    """
    Contain onboarding pages.
    """

    page_1 = models.TextField(blank=True, verbose_name='First Page')
    page_2 = models.TextField(blank=True, verbose_name='Second Page')
    page_3 = models.TextField(blank=True, verbose_name='Third Page')
    page_4 = models.TextField(blank=True, verbose_name='Fourth Page')

    @property
    def first(self):
        if not self.page_1:
            return render_to_string(get_template('page_1'))
        return self.page_1

    @property
    def second(self):
        if not self.page_2:
            return render_to_string(get_template('page_2'))
        return self.page_2

    @property
    def third(self):
        if not self.page_3:
            return render_to_string(get_template('page_3'))
        return self.page_3

    class Meta:
        app_label = 'onboarding'


class UserOnboarding(models.Model):
    """
    Contain history of users onboarding states.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    onboarding = models.ForeignKey(Onboarding, null=True, blank=True, on_delete=models.CASCADE)
    page_1 = models.BooleanField(default=False)
    page_2 = models.BooleanField(default=False)
    page_3 = models.BooleanField(default=False)
    page_4 = models.BooleanField(default=False)

    @classmethod
    def is_passed(cls, user):
        user_onboarding = cls.objects.filter(user=user).first()
        if user_onboarding:
            return user_onboarding.page_1 and user_onboarding.page_2 and user_onboarding.page_3
        return False

    @classmethod
    def update(cls, user, page_number):
        """
        Mark passed onboarding page for current user.
        """
        user_onboarding, _ = cls.objects.update_or_create(user=user, defaults={page_number: True})
        return user_onboarding

    def get_last_passed(self):
        """
        Return last passed user page.
        """
        for num, _ in enumerate(reversed(range(3)), 1):
            field_name = 'page_{}'.format(num)
            if getattr(self, field_name):
                return field_name

    def get_current_page(self):
        """
        Return current page for current user.
        """
        for num, _ in enumerate(range(3), 1):
            field_name = 'page_{}'.format(num)
            if not getattr(self, field_name):
                return field_name
        return 'page_1'

    def are_all_passed(self):
        return all([
            getattr(self, 'page_{}'.format(ind)) for ind, _ in enumerate(range(3), 1)
        ])

    def get_next_page(self, current=None):
        """
        Return next page for current user.
        """
        if current:
            page_number = int(current.split('_')[-1])
            if page_number < 3:
                return 'page_{}'.format(page_number+1)
            else:
                return 'page_1'
        if self.get_last_passed():
            last_passed_number = int(self.get_last_passed().split('_')[-1])
            if last_passed_number < 3:
                return 'page_{}'.format(last_passed_number+1)
        return 'page_1'

    def get_pages(self):
        """
        Return content of onboarding pages.
        """
        return [
            {
                'content': self.onboarding.first if self.onboarding else render_to_string(get_template('page_1')),
                'passed': self.page_1,
                'name': 'page_1'
            },
            {
                'content': self.onboarding.second if self.onboarding else render_to_string(get_template('page_2')),
                'passed': self.page_2,
                'name': 'page_2'
            },
            {
                'content': self.onboarding.third if self.onboarding else render_to_string(get_template('page_3')),
                'passed': self.page_3,
                'name': 'page_3'
            }
        ]

    class Meta:
        app_label = 'onboarding'
