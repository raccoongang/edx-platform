# -*- coding: utf-8 -*-
"""
An API for client-side validation of (potential) user data.
"""

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle

from openedx.core.djangoapps.user_api.accounts.api import (
    get_email_validation_error,
    get_email_existence_validation_error,
    get_confirm_email_validation_error,
    get_country_validation_error,
    get_name_validation_error,
    get_password_validation_error,
    get_username_validation_error,
    get_username_existence_validation_error,
    get_phone_validation_error,
    get_parent_email_validation_error,
    get_parent_phone_validation_error,
    get_instructor_validation_error,
    get_school_city_validation_error,
    get_school_validation_error,
    get_classroom_validation_error
)
from ipware.ip import get_ip


class RegistrationValidationThrottle(AnonRateThrottle):
    """
    Custom throttle rate for /api/user/v1/validation/registration
    endpoint's use case.
    """

    scope = 'registration_validation'

    def get_ident(self, request):
        client_ip = get_ip(request)
        return client_ip


class RegistrationValidationView(APIView):
    """
        **Use Cases**

            Get validation information about user data during registration.
            Client-side may request validation for any number of form fields,
            and the API will return a conclusion from its analysis for each
            input (i.e. valid or not valid, or a custom, detailed message).

        **Example Requests and Responses**

            - Checks the validity of the username and email inputs separately.
            POST /api/user/v1/validation/registration/
            >>> {
            >>>     "username": "hi_im_new",
            >>>     "email": "newguy101@edx.org"
            >>> }
            RESPONSE
            >>> {
            >>>     "validation_decisions": {
            >>>         "username": "",
            >>>         "email": ""
            >>>     }
            >>> }
            Empty strings indicate that there was no problem with the input.

            - Checks the validity of the password field (its validity depends
              upon both the username and password fields, so we need both). If
              only password is input, we don't check for password/username
              compatibility issues.
            POST /api/user/v1/validation/registration/
            >>> {
            >>>     "username": "myname",
            >>>     "password": "myname"
            >>> }
            RESPONSE
            >>> {
            >>>     "validation_decisions": {
            >>>         "username": "",
            >>>         "password": "Password cannot be the same as the username."
            >>>     }
            >>> }

            - Checks the validity of the username, email, and password fields
              separately, and also tells whether an account exists. The password
              field's validity depends upon both the username and password, and
              the account's existence depends upon both the username and email.
            POST /api/user/v1/validation/registration/
            >>> {
            >>>     "username": "hi_im_new",
            >>>     "email": "cto@edx.org",
            >>>     "password": "p"
            >>> }
            RESPONSE
            >>> {
            >>>     "validation_decisions": {
            >>>         "username": "",
            >>>         "email": "It looks like cto@edx.org belongs to an existing account. Try again with a different email address.",
            >>>         "password": "Password must be at least 2 characters long",
            >>>     }
            >>> }
            In this example, username is valid and (we assume) there is
            a preexisting account with that email. The password also seems
            to contain the username.

            Note that a validation decision is returned *for all* inputs, whether
            positive or negative.

        **Available Handlers**

            "name":
                A handler to check the validity of the user's real name.
            "username":
                A handler to check the validity of usernames.
            "email":
                A handler to check the validity of emails.
            "confirm_email":
                A handler to check whether the confirmation email field matches
                the email field.
            "password":
                A handler to check the validity of passwords; a compatibility
                decision with the username is made if it exists in the input.
            "country":
                A handler to check whether the validity of country fields.
    """

    # This end-point is available to anonymous users, so no authentication is needed.
    authentication_classes = []
    throttle_classes = (RegistrationValidationThrottle,)

    def name_handler(self, request):
        name = request.data.get('name')
        return get_name_validation_error(name)

    def username_handler(self, request):
        username = request.data.get('username')
        invalid_username_error = get_username_validation_error(username)
        username_exists_error = get_username_existence_validation_error(username)
        # We prefer seeing for invalidity first.
        # Some invalid usernames (like for superusers) may exist.
        return invalid_username_error or username_exists_error

    def email_handler(self, request):
        email = request.data.get('email')
        invalid_email_error = get_email_validation_error(email)
        email_exists_error = get_email_existence_validation_error(email)
        # We prefer seeing for invalidity first.
        # Some invalid emails (like a blank one for superusers) may exist.
        return invalid_email_error or email_exists_error

    def confirm_email_handler(self, request):
        email = request.data.get('email', None)
        confirm_email = request.data.get('confirm_email')
        return get_confirm_email_validation_error(confirm_email, email)

    def password_handler(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password')
        return get_password_validation_error(password, username)

    def country_handler(self, request):
        country = request.data.get('country')
        return get_country_validation_error(country)
    
    def phone_handler(self, request):
        phone = request.data.get('phone')
        return get_phone_validation_error(phone)
    
    def parent_email_handler(self, request):
        parent_email = request.data.get('parent_email')
        return get_parent_email_validation_error(parent_email)
    
    def parent_phone_handler(self, request):
        parent_phone = request.data.get('parent_phone')
        return get_parent_phone_validation_error(parent_phone)
    
    def instructor_handler(self, request):
        instructor = request.data.get('instructor')
        return get_instructor_validation_error(instructor)

    def school_city_handler(self, request):
        school_city = request.data.get('school_city')
        return get_school_city_validation_error(school_city)

    def school_handler(self, request):
        school = request.data.get('school')
        return get_school_validation_error(school)

    def classroom_handler(self, request):
        classroom = request.data.get('classroom')
        return get_classroom_validation_error(classroom)
        

    validation_handlers = {
        "name": name_handler,
        "username": username_handler,
        "email": email_handler,
        "confirm_email": confirm_email_handler,
        "password": password_handler,
        "country": country_handler,
        "phone": phone_handler,
        "parent_email": parent_email_handler,
        "parent_phone": parent_phone_handler,
        "instructor": instructor_handler,
        "school_city": school_city_handler,
        "school": school_handler,
        "classroom": classroom_handler,
    }

    def post(self, request):
        """
        POST /api/user/v1/validation/registration/

        Expects request of the form
        >>> {
        >>>     "name": "Dan the Validator",
        >>>     "username": "mslm",
        >>>     "email": "mslm@gmail.com",
        >>>     "confirm_email": "mslm@gmail.com",
        >>>     "password": "password123",
        >>>     "country": "PK"
        >>> }
        where each key is the appropriate form field name and the value is
        user input. One may enter individual inputs if needed. Some inputs
        can get extra verification checks if entered along with others,
        like when the password may not equal the username.
        """
        validation_decisions = {}
        for form_field_key in self.validation_handlers:
            # For every field requiring validation from the client,
            # request a decision for it from the appropriate handler.
            if form_field_key in request.data:
                handler = self.validation_handlers[form_field_key]
                validation_decisions.update({
                    form_field_key: handler(self, request)
                })
        return Response({"validation_decisions": validation_decisions})
