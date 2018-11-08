"""
Script for update User's first name, last name  and the name field in UserProfile
"""
import json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from social_django.models import UserSocialAuth


class Command(BaseCommand):
    """
    Update a User's first name, last name  and the name field in UserProfile from remote service .
    """
    help = "Update user's fullname"
 
    def handle(self, *args, **options):
       """
       Realization of the command to update User's first name, last name, and UserProfile's name.
       """
       self.stdout.write("Start to update User's first name, last name, and UserProfile's name field.")
       user_social_auth_list = UserSocialAuth.objects.filter(
           Q(user__first_name='') | Q(user__last_name='') | Q(user__profile__name='')
       ).select_related("user", "user__profile")
       
       if user_social_auth_list.exists():
           
           token_url = '{}/api/v1/user/token.json'.format(settings.FEATURES['DRUPAL_PRIVIDER_URL'])
           auth_url = '{}/api/v1/user/login.json'.format(settings.FEATURES['DRUPAL_PRIVIDER_URL'])
           user_info_url = '{}/api/v1/user/{{}}.json'.format(settings.FEATURES['DRUPAL_PRIVIDER_URL'])
           session = requests.session()
           session.headers['Content-type'] = 'application/json'
    
           try:
               r = session.post(token_url)
               csrf_token = None
               if r.ok:
                   self.stdout.write('Get the API token')
                   csrf_token = r.json().get('token')
        
               if csrf_token:
                   self.stdout.write('Post API auth data')
                   session.headers['X-CSRF-Token'] = csrf_token
                   r = session.post(auth_url, data=json.dumps({
                       'username': settings.FEATURES['DRUPAL_API_USER'],
                       'password': settings.FEATURES['DRUPAL_API_PASSWORD']
                   }))
            
                   if r.ok:
                       self.stdout.write('Update users')
                       for social_auth_user in user_social_auth_list:
                           try:
                               with transaction.atomic():
                                   r = session.get(user_info_url.format(social_auth_user.uid))
                                   api_data = r.ok and r.json() or {}
                                   if api_data:
                                       full_name = (
                                               api_data.get('field_full_name', {}) or {}
                                       ).get('und', [{}])[0].get('value', '')
                                       first_name = (
                                               api_data.get('field_first_name', {}) or {}
                                       ).get('und', [{}])[0].get('value', '')
                                       last_name = (
                                               api_data.get('field_last_name', {}) or {}
                                       ).get('und', [{}])[0].get('value', '')
                                       if not (first_name and last_name) and full_name:
                                           full_name_list = full_name.split()
                                           fname, lname = (full_name_list[0], ' '.join(full_name_list[1:]))
                                           first_name = first_name or fname
                                           last_name = last_name or lname
                                           
                                       if not full_name and (first_name or last_name ):
                                           full_name = "{} {}".format(first_name, last_name).strip()
                                       social_auth_user.user.profile.name = full_name
                                       social_auth_user.user.profile.save()
                                       social_auth_user.user.first_name = first_name
                                       social_auth_user.user.last_name = last_name
                                       social_auth_user.user.save()
                                       self.stdout.write(
                                           "User with id {} updated: full_name {}, first_name {}, last_name {}".format(
                                               social_auth_user.user.id, full_name, first_name, last_name
                                           )
                                       )
                                   else:
                                       self.stdout.write(
                                           "Remote service returned empty response for user:id={}, uid={}".format(
                                               social_auth_user.user.id, social_auth_user.uid
                                           )
                                       )
                           except Exception as e:
                               if hasattr(e, 'message'):
                                   error_string = e.message
                               else:
                                   error_string = str(e)
                               self.stdout.write(
                                   "User with id {} not updated. Exception {}".format(
                                       social_auth_user.user.id, error_string
                                   )
                               )
               self.stdout.write("Done")
           except Exception as e:
               if hasattr(e, 'message'):
                   error_string = e.message
               else:
                   error_string = str(e)
               self.stdout.write('Exception {}'.format(error_string))
