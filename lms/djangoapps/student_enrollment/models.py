from django.db import models
from django.contrib.auth.models import User
from ci_program.models import Program


class ProgramAccessStatus(models.Model):
    """
    Store a student's access to a program. This will allow us to
    determine (mostly at the time of login), whether or not a student
    can access the LMS.

    `user` references the user in question
    `program_access` is a boolean that indicates whether or the user
        can gain access to the LMS
    """

    user = models.ForeignKey(User)
    program_access = models.BooleanField()

    def __unicode__(self):
        return "Program is accessible for {}: {}".format(
            self.user, self.program_access)
    
    def set_access_level(self, user, allowed_access):
        access = self(user=user, program_access=allowed_access)
        access.save()

ENROLLMENT_TYPES = (
    (0, "Enrollment"),
    (1, "Un-enrollment"),
    (2, "Re-enrollment")
)


class EnrollmentStatusHistory(models.Model):
    """
    Store a historical record of everytime the system attempted
    to register and enroll a student in a course.

    `student` is a reference to the student
    `program` is a reference to the program
    `registered` is a boolean value used to indicate whether or not the
        registration was successful
    `enrollment_type` is a choice field used to determine if the student
        was enrolled, unenrolled or re-enrolled
    `enrolled` is a boolean value used to indicate whether or not the
        enrollment was successful
    `email_sent` is a boolean value used to indicate whether or not the
        email was successfully sent to the student
    `enrollment_attempt` is the time at which the attempt occurred
    """
    
    student = models.ForeignKey(User)
    program = models.ForeignKey(Program)
    registered = models.BooleanField(null=False, blank=False)
    enrollment_type = models.IntegerField(choices=ENROLLMENT_TYPES)
    enrolled = models.BooleanField(null=False, blank=False)
    email_sent = models.BooleanField(null=False, blank=False)
    enrollment_attempt = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        if self.registered and self.enrolled and self.email_sent:
            return "{} process for {} was successfully completed at {}".format(
                self.get_enrollment_type_display(), self.student, self.enrollment_attempt) 
        else:
            return "{} process for {} was unsuccessful".format(
                self.enrollment_type, self.student) 