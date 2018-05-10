from uuid import uuid4
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.mail import send_mail
from opaque_keys.edx.locator import CourseLocator
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from student.models import CourseEnrollmentAllowed
from lms.djangoapps.instructor.enrollment import enroll_email, unenroll_email
from lms.djangoapps.student_enrollment.utils import create_email_connection
from lms.djangoapps.student_enrollment.utils import constuct_email


def _choices(*values):
    """
    Helper for use with model field 'choices'.
    """
    return [(value, ) * 2 for value in values]


class Program(TimeStampedModel):
    """
    Representation of a Program.
    """

    uuid = models.UUIDField(
        blank=True,
        default=uuid4,
        editable=False,
        unique=True,
    )

    name = models.CharField(
        help_text=_('The user-facing display name for this Program.'),
        max_length=255,
        unique=True,
    )

    subtitle = models.CharField(
        help_text=_('A brief, descriptive subtitle for the Program.'),
        max_length=255,
        blank=True,
    )

    marketing_slug = models.CharField(
        help_text=_('Slug used to generate links to the marketing site'),
        blank=True,
        max_length=255
    )

    number_of_modules = models.IntegerField(null=True, blank=True)
    length_of_program = models.CharField(max_length=25, null=True, blank=True)
    effort = models.CharField(max_length=25, null=True, blank=True)
    full_description = models.TextField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    zoho_program_code = models.CharField(max_length=50, null=True, blank=True)
    enrolled_students = models.ManyToManyField(User)

    def __unicode__(self):
        return unicode(self.name)
    
    def get_course_locators(self):
        list_of_locators = []
        
        for course_code in self.course_codes.all():
            course_identifiers = course_code.key.split('+')
            list_of_locators.append(CourseLocator(course_identifiers[0],
                course_identifiers[1], course_identifiers[2]))
        
        return list_of_locators
    
    def get_courses(self):
        """
        Get the list of courses in the program instance based on their
        course codes.

        `self` is the specific program instance

        Returns the list of children courses
        """
        
        list_of_courses = []
        
        for course_code in self.course_codes.all():
            course_identifiers = course_code.key.split('+')
            locator = CourseLocator(course_identifiers[0], course_identifiers[1], course_identifiers[2])
            list_of_courses.append(CourseOverview.objects.get(id=locator))

        return list_of_courses
    
    def send_email(self, student, enrollment_type, password):
        """
        Send the enrollment email to the student.

        `student` is an instance of the user object
        `program_name` is the name of the program that the student is
            being enrolled in
        `password` is the password that has been generated. Sometimes
            this will be externally, or the student may already be
            aware of their password, in which case the value will be
            None

        Returns True if the email was successfully sent, otherwise
            return False
        """

        # Set the values that will be used for sending the email
        to_address = student.email
        from_address = 'learning@codeinstitute.net'
        student_password = password
        
        if enrollment_type == 0:
            subject = "You have been enrolled in your Code Institute {} program".format(
                self.name)
            template_location = "emails/enrollment_email.html"
        elif enrollment_type == 1:
            subject = "Code Institute Unenrollment"
            template_location = "emails/unenrollment_email.html"
        elif enrollment_type == 2:
            subject = "You have been re-enrolled!"
            template_location = "emails/reenrollment_email.html"
        
        if self.name == "5 Day Coding Challenge":
            module_url = "https://courses.codeinstitute.net/courses/%s/course/" % self.course_codes.first().key
        else:
            module_url = None
        
        # Construct the email using the information provided
        email_content = constuct_email(to_address, from_address,
                                       template_location,
                                       student_password=password,
                                       program_name=self.name,
                                       module_url=module_url)
        
        # Create a new email connection
        email_connection = create_email_connection()

        # Send the email. `send_mail` will return the amount of emails
        # that were sent successfully. We'll use this number to determine
        # whether of not the email status is to be set as `True` or `False`
        number_of_mails_sent = send_mail(subject, email_content,
                                            from_address, [to_address],
                                            fail_silently=False,
                                            html_message=email_content,
                                            connection=email_connection)
        
        return True if number_of_mails_sent == 1 else False
        
    
    def enroll_student_in_program(self, student):
        """
        Enroll a student in a program.

        This works by getting all of the courses in a program and enrolling
        the student in each course in the program. Then add the student to
        the `enrolled_students` table.

        `student` is the user instance that we which to enroll in the program

        Returns True if the student was successfully enrolled in all of the courses,
            otherwise return False
        """
        for course in self.get_courses():
            enroll_email(course.id, student.email, auto_enroll=True)
            cea, _ = CourseEnrollmentAllowed.objects.get_or_create(
                course_id=course.id, email=student.email)
            cea.auto_enroll = True
            cea.save()

        self.enrolled_students.add(User.objects.get(email=student.email))
        
        return True if student.courseenrollment_set.all().count() == self.number_of_modules else False
    
    def unenroll_student_from_program(self, student):
        """
        Unenroll a student from a program.

        This works by getting all of the courses in a program and unenrolling
        the student from each course in the program. Then remove the student to
        the `enrolled_students` table.

        `student` is the user instance that we which to enroll in the program

        Returns True if the student was successfully unenrolled from all of the courses,
            otherwise return False
        """
        for course in self.get_courses():
            unenroll_email(course.id, student.email)
        
        self.enrolled_students.remove(User.objects.get(email=student.email))
        
        enrolled_courses = student.courseenrollment_set.all()

        cea = CourseEnrollmentAllowed.objects.filter(email=student.email).delete()
        
        return True if cea is None else False


class CourseCode(models.Model):
    """
    Store the key and a display names for each course that belongs to a program 
    """
    key = models.CharField(
        help_text="The 'course' part of course_keys associated with this course code, "
                  "for example 'DemoX' in 'edX/DemoX/Demo_Course'.",
        max_length=128
    )
    display_name = models.CharField(
        help_text=_('The display name of this course code.'),
        max_length=128,
    )
    programs = models.ManyToManyField(Program, related_name='course_codes', through='ProgramCourseCode')

    def __unicode__(self):
        return unicode(self.display_name)


class ProgramCourseCode(TimeStampedModel):
    """
    Represents the many-to-many association of a course code with a program.
    """
    program = models.ForeignKey(Program)
    course_code = models.ForeignKey(CourseCode)
    position = models.IntegerField()

    class Meta(object):  # pylint: disable=missing-docstring
        ordering = ['position']

    def __unicode__(self):
        return unicode(self.course_code)

    def save(self, *a, **kw):
        """
        Override save() to validate m2m cardinality and automatically set the position for a new row.
        """
        if self.position is None:
            # before creating, ensure that the program has an association with the same org as this course code
            if not ProgramOrganization.objects.filter(
                    program=self.program, organization=self.course_code.organization).exists():
                raise ValidationError(_('Course code must be offered by the same organization offering the program.'))
            # automatically set position attribute for a new row
            res = ProgramCourseCode.objects.filter(program=self.program).aggregate(max_position=models.Max('position'))
            self.position = (res['max_position'] or 0) + 1
        return super(ProgramCourseCode, self).save(*a, **kw)
