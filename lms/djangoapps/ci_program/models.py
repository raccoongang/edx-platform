from logging import getLogger
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
from lms.djangoapps.student_enrollment.utils import construct_email
from lms.djangoapps.courseware.courses import get_course
from openedx.core.lib.courses import course_image_url

log = getLogger(__name__)


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

    length_of_program = models.CharField(max_length=25, null=True, blank=True)
    effort = models.CharField(max_length=25, null=True, blank=True)
    full_description = models.TextField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    program_code = models.CharField(max_length=50, null=True, blank=True)
    enrolled_students = models.ManyToManyField(
        User, blank=True)
    program_code_friendly_name = models.CharField(max_length=50, null=True, blank=True)
    
    @property
    def number_of_modules(self):
        """
        Get the length of a program - i.e. the number of modules
        """
        return len(self.get_courses())
    
    @property
    def email_template_location(self):
        """
        Each program has it's own ecosystem and branding. As such, each
        program will have it's very own branded email. In addition to this,
        different emails can be sent for different types of enrollment.
        
        A program's enrollment emails should be located in their own directory
        in the theme's code base. Using the `program_code_friendly_name` we can
        target the necessary directory and the enrollment_type specfic email
        and the relevant subject
        """
        
        # Use the enrollment type to determine which email should be sent - 
        # i.e. enrollment, unenrollment & reenrollment, along with the
        # accompany subject
        if self.enrollment_type == 0:
            subject = "You have been enrolled in your Code Institute {} program".format(
                self.name)
            template_type_name = "enrollment_email.html"
        elif self.enrollment_type == 1:
            subject = "Code Institute Unenrollment"
            template_type_name = "unenrollment_email.html"
        elif self.enrollment_type == 2:
            subject = "You have been re-enrolled!"
            template_type_name = "reenrollment_email.html"
        elif self.enrollment_type == 3:
            subject = "You have been enrolled in your Code Institute {} program".format(
                self.name)
            template_type_name = "upgrade_enrollment_email.html"
        
        # Get the name of the directory where the program's emails are
        # stored
        template_dir_name = self.program_code_friendly_name
        
        # Now use the above information to generate the path the email
        # template
        template_location = 'emails/{0}/{1}'.format(
            template_dir_name, template_type_name)
        
        return template_location, subject

    def __unicode__(self):
        return unicode(self.name)
    
    def get_program_descriptor(self, user):
        """
        The program descriptor will return all of necessary courseware
        info for a given program. The information contained in the descriptor
        should include -
        
          - Name
          - Subtitle
          - Full description
          - Image
          - Video
          - Length
          - Effort
          - Number of modules
          - Modules
            - Name
            - Short Description
            - Key
            - Image
        """
        
        courses = []
        
        # Gather the basic information about the program
        name = self.name
        subtitle = self.subtitle
        full_description = self.full_description
        image = self.image
        video = self.video
        length = self.length_of_program
        effort = self.effort
        number_of_modules = self.number_of_modules
        
        # Gather the information of each of the modules in the program
        if self.program_code == "5DCC":
            student = User.objects.get(email=user.email)
            users_five_day_module = student.courseenrollment_set.filter(
                course_id__icontains="dcc").order_by('created').last()
            course_id = users_five_day_module.course_id
            course_overview = CourseOverview.objects.get(id=course_id)
            course_descriptor = get_course(course_id)
            
            courses.append({
                    "course_key": course_id,
                    "course": course_overview,
                    "course_image": course_image_url(course_descriptor)
                })
        else:    
            for course_overview in self.get_courses():
                course_id = course_overview.id
                course_descriptor = get_course(course_id)
                
                courses.append({
                    "course_key": course_id,
                    "course": course_overview,
                    "course_image": course_image_url(course_descriptor)
                })
        
        # Create a dict out the information gathered
        program_descriptor = {
            "name": name,
            "subtitle": subtitle,
            "full_description": full_description,
            "image": image,
            "video": video,
            "length": length,
            "effort": effort,
            "number_of_modules": number_of_modules,
            "modules": courses
        }
        
        return program_descriptor
    
    def get_course_locators(self):
        """
        Get the list of locators for each of the modules in a program
        """
        list_of_locators = []
        
        for course_code in self.course_codes.all():
            course_identifiers = course_code.key.split('+')
            list_of_locators.append(CourseLocator(
                course_identifiers[0],
                course_identifiers[1],
                course_identifiers[2]
            ))
        
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
            locator = CourseLocator(
                course_identifiers[0],
                course_identifiers[1],
                course_identifiers[2]
            )
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
        
        self.enrollment_type = enrollment_type
        
        if self.name == "Five Day Coding Challenge":
            module_url = "https://courses.codeinstitute.net/courses/{}/course/".format(
                self.course_codes.first().key)
        else:
            module_url = None
        
        # Get the email location & subject
        template_location, subject = self.email_template_location
        
        # Construct the email using the information provided
        email_content = construct_email(to_address, from_address,
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
        
        email_successfully_sent = None
        log_message = ""
        
        if number_of_mails_sent == 1:
            email_successfully_sent = True
            log_message = "Email successfully sent to %s" % to_address
        else:
            email_successfully_sent = False
            log_message = "Failed to send email to %s" % to_address
        
        log.info(log_message)

        return email_successfully_sent

    def enroll_student_in_program(self, student_email):
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
            enroll_email(course.id, student_email, auto_enroll=True)
            cea, _ = CourseEnrollmentAllowed.objects.get_or_create(
                course_id=course.id, email=student_email)
            cea.auto_enroll = True
            cea.save()
        
        student_to_be_enrolled = User.objects.get(email=student_email)

        self.enrolled_students.add(student_to_be_enrolled)
        
        student_successfully_enrolled = None
        log_message = ""
        
        if self.enrolled_students.filter(email=student_email).exists():
            student_successfully_enrolled = True
            log_message = "%s was enrolled in %s" % (
                student_email, self.name)
        else:
            student_successfully_enrolled = False
            log_message = "Failed to enroll %s in %s" % (
                student_email, self.name)
        
        log.info(log_message)
        return student_successfully_enrolled
    
    def unenroll_student_from_program(self, student):
        """
        Unenroll a student from a program.

        This works by getting all of the courses in a program and unenrolling
        the student from each course in the program. Then remove the student to
        the `enrolled_students` table.

        `student` is the user instance that we which to enroll in the program

        Returns True if the student was successfully unenrolled from all of the courses,
            otherwise, return False
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
    programs = models.ManyToManyField(
        Program, related_name='course_codes', through='ProgramCourseCode')

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