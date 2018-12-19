from django import forms
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from web_science.models import WebScienceCourseOverview
from xmodule.modulestore.django import modulestore


class WebScienceCourseOverviewForm(forms.ModelForm):
    """
    Form Settings for Web Science courses
    """
    course = forms.CharField()

    def clean_course(self):
        """
        Validate the course id
        """
        cleaned_data = super(WebScienceCourseOverviewForm, self).clean()
        cleaned_id = cleaned_data['course']

        try:
            course_key = CourseKey.from_string(cleaned_id)
        except (InvalidKeyError, CourseOverview.DoesNotExist):
            msg = u'Course id invalid. Entered course id was: "{0}".'.format(cleaned_id)
            raise forms.ValidationError(msg)

        if not modulestore().has_course(course_key):
            msg = u'Course not found. Entered course id was: "{0}".'.format(cleaned_id)
            raise forms.ValidationError(msg)

        return course_key

    class Meta(object):
        model = WebScienceCourseOverview
        fields = (
            'course',
            'color',
            'image',
        )
