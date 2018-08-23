from django import forms
from django.utils.translation import ugettext as _
from collections import OrderedDict

I_AM_A = OrderedDict(
    (
        ('', '-- select --'),
        ('student', _("Student")),
        ('professor', _("Professor")),
        ('journalist', _("Journalist")),
        ('administrator', _("University Administrator")),
        ('other', _("Other")),
    )
)

INQUIRY_TYPE = OrderedDict(
    (
        ('', '-- select --'),
        ('registration', _("Question about Registration and Activation")),
        ('technical', _("I am having a Technology Problem")),
        ('accessibility', _("Question about Accessibility for students with disabilities")),
        ('exams', _("Question about Certification and Exams")),
        ('account', _("My account details need changing")),
        ('university', _("Business development / Institutional inquiry")),
        ('harrassment', _("Report unethical or harassing conduct")),
        ('other', _("Other")),
    )
)


class ContactForm(forms.Form):
    email = forms.EmailField(label=_('You e-mail'), max_length=255)
    full_name = forms.CharField(label=_('Full name'), max_length=255)
    phone = forms.CharField(label=_('You phone'), max_length=16, required=False)
    i_am_a = forms.ChoiceField(choices=I_AM_A.items(), required=True)
    inquiry_type = forms.ChoiceField(choices=INQUIRY_TYPE.items(), required=True)
    message = forms.CharField(label=_('Message'), widget=forms.Textarea)

    @property
    def get_data(self):
        base_result = self.cleaned_data
        base_result['i_am_a'] = I_AM_A[base_result['i_am_a']]
        base_result['inquiry_type'] = INQUIRY_TYPE[base_result['inquiry_type']]
        return base_result

    def as_ul_with_class(self, css_classes):
        "Return this form rendered as HTML <li class=''>s -- excluding the <ul></ul>."
        return self._html_output(
            normal_row=(
                '<li class="{css_classes}">%(errors)s%(label)s %(field)s%(help_text)s</li>'.
                format(css_classes=css_classes)
            ),
            error_row='<li>%s</li>',
            row_ender='</li>',
            help_text_html='<span class="helptext">%s</span>',
            errors_on_separate_row=False,
        )

    def save(self):
        raise NotImplementedError
