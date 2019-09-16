from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse as api_reverse
from rest_framework.test import APITestCase
from social_django.models import UserSocialAuth
from  copy import copy
from student.models import UserProfile
from third_party_auth.models import OAuth2ProviderConfig


class UserAPITestCase(APITestCase):
    """
    Test for user registration API.
    """

    allow_database_queries = True

    def setUp(self):
        self.user_email = "i-am-username@gmail.com"
        self.social_uid = "external-uid"
        self.provider = "custom-backend"
        self.url = api_reverse("ucdc_edx_api:user_create")
        self.username = "i-am-username"
        OAuth2ProviderConfig.objects.create(
            backend_name=self.provider, key="custom-key", secret="custom-secret"
        )

    @override_settings(EDX_API_KEY="key")
    def test_should_register_user_successfully(self):
        data = {"username": self.username, "email": self.user_email, "uid": self.social_uid}
        self.client.credentials(HTTP_X_EDX_API_KEY="key")
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["id"])
        self.assertEqual(response.data["email"], self.user_email)

        user = User.objects.get(id=response.data["id"])
        self.assertEqual(user.email, self.user_email)
        self.assertTrue(isinstance(user.profile, UserProfile))

        social_auth = UserSocialAuth.objects.get(user=user)
        self.assertEqual(social_auth.provider, self.provider)
        self.assertEqual(social_auth.uid, self.social_uid)

    @override_settings(EDX_API_KEY="key")
    def test_should_fail_registration_when_account_exist(self):
        data = {"username": self.username, "email": self.user_email, "uid": self.social_uid}
        self.client.credentials(HTTP_X_EDX_API_KEY="key")
        self.client.post(self.url, data, format="json") # should create user account

        # repeat request when payload is the same
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # repeat request when email is not uniq
        data["username"] = "a-new-username"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # repeat request when uid is not uniq
        data["email"] = "new-username@gmail.com"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(EDX_API_KEY="key")
    def test_should_fail_registration_if_payload_is_incorrect(self):
        data = {"username": self.username, "email": self.user_email, "uid": self.social_uid}

        # request without HTTP_X_EDX_API_KEY
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_X_EDX_API_KEY="key")

        # request when username is incorrect
        data_ = copy(data)
        data_['username'] = "bla.bla bla"
        response = self.client.post(self.url, data_, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # request when email is incorrect
        data_ = copy(data)
        data_['email'] = "bla.bla bla"
        response = self.client.post(self.url, data_, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # request without uid
        data.pop("uid")
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


