"""
Script for update User's first name, last name  and the name field in UserProfile
"""
import json
from logging import getLogger

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from social_django.models import UserSocialAuth

log = getLogger(__name__)


class Command(BaseCommand):
    """
    Update a User's first name, last name  and the name field in UserProfile from remote service .
    """
    help = "Update user's fullname"
 
    def handle(self, *args, **options):
       """
       Realisation the command to update User's first name, last name  and the name field in UserProfile.
       """
       self.stdout.write("Start to update User's first name and last name  and the name field in UserProfile")
       user_social_auth_list = UserSocialAuth.objects.filter(
           Q(user__first_name__icontains='') | Q(user__last_name__icontains='') | Q(user__profile__name__icontains='')
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
                   log.info('Get the API token')
                   csrf_token = r.json().get('token')
        
               if csrf_token:
                   log.info('Post API auth data')
                   session.headers['X-CSRF-Token'] = csrf_token
                   r = session.post(auth_url, data=json.dumps({
                       'username': settings.FEATURES['DRUPAL_API_USER'],
                       'password': settings.FEATURES['DRUPAL_API_PASSWORD']
                   }))
            
                   if r.ok:
                       for social_auth_user in user_social_auth_list:
                           with transaction.atomic():
                               r = session.get(user_info_url.format(social_auth_user.uid))
                               api_data = r.ok and r.json() or {}
                               full_name = (api_data.get('field_full_name', {}) or {}).get('und', [{}])[0].get('value', '')
                               social_auth_user.user.profile.name = full_name
                               social_auth_user.user.profile.save()
                               full_name_list = full_name.split()
                               fname, lname = full_name_list and (full_name_list[0], ' '.join(full_name_list[1:])) or ('', '')
                               social_auth_user.user.first_name = fname
                               social_auth_user.user.last_name = lname
                               social_auth_user.user.save()
                               self.stdout.write("User {} updated".format(full_name))
           except Exception as e:
               log.error('Exception %s', e)
               raise e
        
       self.stdout.write("Done")
