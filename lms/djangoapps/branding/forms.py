from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _


CATEGORY_CHOICES = (
(_('Sign In'), (
   ('password', _('Password could not be restored')),
   ('cant_login', _('I can not login')),
  )
),
(_('Review of courses'), (
   ('register_unable', _('Unable to register for courses')),
   ('course_start', _('You can not start or cancel the registration of courses')),
  )
),
(_('Certificates'), (
   ('certificate_issue', _('Unable to issue certificate')),
   ('certificate_not_match', _('The certificate does not match the course or the name is different')),
  )
),
(_('Course Content Review'), (
   ('video_not_working', _('Video - does not work')),
   ('image_not_working', _('Images - Do not appear on the screen')),
   ('question_no_answer', _('Questions - Do not accept answers')),
   ('question_no_apper', _('Questions - Do not appear on the screen')),
   ('question_no_register', _('Questions - Do not register as a marker')),
   ('activity_no_interact', _('Activities - Do not interact with the user')),
   ('exam_closed', _('Examinations - Closed after the date of issuance')),
   ('exam_cant_submit', _('Exams - can not be submitted')),
   ('discussion_problem', _('Discussion Forum - Questions could not be asked or answered')),
  )
),

   ('others', _('Others')),
)

class ContactForm(forms.Form):
    name = forms.CharField(label=_('You name'), max_length=255)
    email = forms.EmailField(label=_('You e-mail'), max_length=255)
    subject = forms.CharField(label=_('Subject'), max_length=255)
    phone = forms.CharField(label=_('You phone'), required=False,
        validators=[RegexValidator(r'^\d{6,10}$', _("The phone number must be greater than 6 and less than 10 digits only."))]
    )
    category = forms.CharField(label=_("Problem's category"), widget=forms.Select(choices=CATEGORY_CHOICES, attrs={'class':'input-block'}), required=False)
    message = forms.CharField(label=_('Message'), widget=forms.Textarea, required=False)

    def save(self):
        if self.is_valid():
            separator = '-' * 16
            message = '{}\n{}\n{}\n{}\n\n{}'.format(
                self.cleaned_data['name'],
                self.cleaned_data['email'],
                self.cleaned_data['phone'],
                self.cleaned_data['category'],
                separator,
                self.cleaned_data['message']
            )
            send_mail(self.cleaned_data['subject'], message, settings.DEFAULT_FROM_EMAIL, [settings.CONTACT_EMAIL])
            return True
        return False
