"""
Script for migrating phone field from custom table to UserProfile.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction

from student.models import UserProfile


class Command(BaseCommand):
    """
    Update a UserProfile's phone field from custom_reg_form_extrainfo table.
    """
    help = 'Update userprofile phone field from custom_reg_form_extrainfo'
 
    def handle(self, *args, **options):
       """
       Realisation the command to update a phone field in a UserProfile object.
       """
       self.stdout.write("Start to update a phone field in a User Profile")
       user_profiles = UserProfile.objects.filter(user__is_active=True).select_related("user")
       for user_profile in user_profiles:
           with transaction.atomic():
               with connections['default'].cursor() as cursor:
                   cursor.execute(
                       "SELECT phone FROM custom_reg_form_extrainfo WHERE user_id = {}".format(user_profile.user.id)
                   )
                   phone = cursor.fetchone()
                   if phone:
                       user_profile.phone = phone[0]
                       user_profile.save()
                       self.stdout.write(
                           "User id: {user_id}  phone: {phone}".format(user_id=user_profile.user.id, phone=phone[0])
                       )
       self.stdout.write("Done")
