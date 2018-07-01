from rest_framework import serializers


class EnrollmentSerializer(serializers.Serializer):
    """
    The serializer used to deserialize incoming user enrollment data.
    This data doesn't map directly to a model as it just needs to satisfy
    a minumum set of requirements in order to enroll a student into a
    program.

    These requirements are:

    `email` is the email address that we'll assign to the user upon registration
    `full_name` is the full name of the user that is being enrolled. This will be
        used to create a username
    `course_code` is the code used to identify a program in the database
    `manual_override` is used to allow the enrollment to occur outside
        of the normal permitted time (Mondays)
    """

    email = serializers.EmailField(max_length=128, required=True)
    full_name = serializers.CharField(max_length=128, required=True)
    course_code = serializers.CharField(max_length=50, required=True)
    manual_override = serializers.BooleanField()
