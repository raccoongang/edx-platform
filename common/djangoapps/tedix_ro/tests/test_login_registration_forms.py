"""Tests for the login and registration form rendering. """
from ddt import data, ddt, unpack
from django.contrib.auth.models import User
from django.test import TestCase


from tedix_ro.forms import StudentRegisterForm, InstructorRegisterForm
from tedix_ro.models import City, Classroom, InstructorProfile, School


@ddt
class StudentRegisterFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='user',
            email='user@test.test',
            password='test',
            is_staff=True,
            is_active=True
        )
        cls.city = City.objects.create(name='city')
        cls.school = School.objects.create(
            name='school',
            city=cls.city,
            school_type='Public'
        )
        cls.instructor = InstructorProfile.objects.create(
            school_city=cls.city,
            school=cls.school,
            user=cls.user,
            phone='1234567890',
        )
        cls.classroom = Classroom.objects.create(name='classroom')

    @data(
        {
            'role': 'student',
            'email': 'student@example.com',
            'name': 'student',
            'username': 'student',
            'parent_phone': '1234567890',
            'parent_email': 'parent@example.com',
            'phone': '1234567891',
        },
        # test the valid creation of a unique username for the parent email
        {
            'role': 'student',
            'email': 'student@example.com',
            'name': 'student',
            'username': 'uniqusername',
            'parent_phone': '1234567890',
            'parent_email': 'uniqusername@example.com', 
            'phone': '1234567891',
        }
    )
    def test_form_valid(self, data):
        print(data)
        data.update({
            'school': int(self.school.id),
            'school_city': int(self.city.id),
            'instructor': int(self.instructor.id),
            'classroom': int(self.classroom.id),
        })
        form = StudentRegisterForm(data)
        self.assertTrue(form.is_valid())

    def test_different_student_and_parent_email(self):
        form = StudentRegisterForm({
            'email': 'user123@example.com',
            'parent_email': 'user123@example.com'
        })
        message_error = 'Student and parent emails must be different.'
        self.assertFalse(form.is_valid())
        self.assertIn(message_error, form.errors.get('parent_email'))

    def test_different_student_and_parent_phone(self):
        form = StudentRegisterForm({
            'phone': '1234567890',
            'parent_phone': '1234567890'
        })
        message_error = 'Student and parent phone numbers must be different.'
        self.assertFalse(form.is_valid())
        self.assertIn(message_error, form.errors.get('parent_phone'))

    @unpack
    @data(
        {'field': 'parent_email', 'value': '', 'message_error': 'Please enter your parent email.'},
        {'field': 'parent_email', 'value': 'abcd', 'message_error': 'Enter a valid email address.'},

        {'field': 'classroom', 'value': 9999, 'message_error': 'Select a valid choice. That choice is not one of the available choices.'},
        
        {'field': 'school_city', 'value': '', 'message_error': 'Please select your city.'},
        {'field': 'school_city', 'value': 9999, 'message_error': 'Select a valid choice. That choice is not one of the available choices.'},
        
        {'field': 'school', 'value': '', 'message_error': 'Please select your school.'},
        {'field': 'school', 'value': 9999, 'message_error': 'Select a valid choice. That choice is not one of the available choices.'},
        
        {'field': 'phone', 'value': '', 'message_error': 'Please enter your phone number.'},
        {'field': 'phone', 'value': 'asdfasdfasdf', 'message_error': 'The phone number length must be from 10 to 15 digits.'},
        {'field': 'phone', 'value': '123456789', 'message_error': 'The phone number length must be from 10 to 15 digits.'},
        {'field': 'phone', 'value': '1234567890123456', 'message_error': 'The phone number length must be from 10 to 15 digits.'},
        
        {'field': 'parent_phone', 'value': '', 'message_error': 'Please enter your parent phone number.'},
        {'field': 'parent_phone', 'value': '123456789', 'message_error': 'The parent phone number length must be from 10 to 15 digits.'},
        {'field': 'parent_phone', 'value': '1234567890123456', 'message_error': 'The parent phone number length must be from 10 to 15 digits.'},
    )
    def test_field_validation(self, field, value, message_error):
        form = StudentRegisterForm({field: value})
        self.assertFalse(form.is_valid())
        self.assertIn(message_error, form.errors.get(field))


@ddt
class InstructorRegisterFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='user',
            email='user@test.test',
            password='test',
            is_staff=True,
            is_active=True
        )
        cls.city = City.objects.create(name='city')
        cls.school = School.objects.create(
            name='school',
            city=cls.city,
            school_type='Public'
        )
        cls.instructor = InstructorProfile.objects.create(
            school_city=cls.city,
            school=cls.school,
            user=cls.user,
            phone='1234567890',
        )
        cls.classroom = Classroom.objects.create(name='classroom')

    def test_form_valid(self):
        data = {
            'role': 'instructor',
            'email': 'instructor@example.com',
            'name': 'instructor',
            'username': 'instructor',
            'classroom': int(self.classroom.id),
            'phone': '1234567891',
            'school_city': int(self.city.id),
            'school': int(self.school.id),
        }
        form = InstructorRegisterForm(data)
        self.assertTrue(form.is_valid())

    @unpack
    @data(
        {'field': 'school_city', 'value': '', 'message_error': 'Please select your city.'},
        {'field': 'school_city', 'value': 9999, 'message_error': 'Select a valid choice. That choice is not one of the available choices.'},
        
        {'field': 'school', 'value': '', 'message_error': 'Please select your school.'},
        {'field': 'school', 'value': 9999, 'message_error': 'Select a valid choice. That choice is not one of the available choices.'},
        
        {'field': 'phone', 'value': '', 'message_error': 'Please enter your phone number.'},
        {'field': 'phone', 'value': 'asdfasdfasdf', 'message_error': 'The phone number length must be from 10 to 15 digits.'},
        {'field': 'phone', 'value': '123456789', 'message_error': 'The phone number length must be from 10 to 15 digits.'},
        {'field': 'phone', 'value': '1234567890123456', 'message_error': 'The phone number length must be from 10 to 15 digits.'},
    )
    def test_field_validation(self, field, value, message_error):
        form = InstructorRegisterForm({field: value})
        self.assertFalse(form.is_valid())
        self.assertIn(message_error, form.errors.get(field))
