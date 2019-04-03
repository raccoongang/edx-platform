from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_noop
# Backwards compatible settings.AUTH_USER_MODEL
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class case_study_abstracts(models.Model):
    """
    This model contains two extra fields that will be saved when a user registers.
    The form that wraps this model is in the forms.py file.
    """
    user = models.ForeignKey(USER_MODEL, null=False, related_name='case_study_abstracts')

    title = models.CharField(max_length=255, db_index=True,null=False)

    description = models.TextField(blank=True)
    uploaded_file = models.CharField(blank=True, max_length=500, db_index=True)

    USER_TYPE = (
        ('dr', ugettext_noop('Doctor')),
        ('prof', ugettext_noop('Professor')),
        ('std', ugettext_noop('Student')),
        ('team', ugettext_noop('Team'))
    )
    user_type = models.CharField(
        default='dr', null=False, max_length=5, db_index=True, choices=USER_TYPE
    )

    CASE_STUDY_TYPE = (
        ('Observational (non-experimental) studies',
            (
                ('chrt-stds', 'Cohort studies'),
                ('case-cntrl', 'Case control studies'),
                ('rdbs', 'Routine-data-based studies'),
                ('drs', 'Dose-response studies'),
            )
        ),
        ('Intervention (experimental) studies',
            (
                ('cl', 'Clinical trials'),
                ('fli', 'Field trials(individual level)'),
                ('fla', 'Field trials(aggregated level)')
            )
        ),        
    )

    case_study_type = models.CharField(
        null=False, max_length=10, db_index=True, choices=CASE_STUDY_TYPE
    )
    author_name = models.CharField(null=True, max_length=500,blank=True)
    author_email = models.CharField(null=True, max_length=500,blank=True)
    author_affiliation = models.CharField(null=True, max_length=500,blank=True)
    tos = models.CharField(null=True, max_length=5,blank=True)
    csa_updated = models.DateTimeField(auto_now=True)
    csa_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{}".format(self.user)
