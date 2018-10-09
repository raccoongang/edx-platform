"""
Script for migrate phone from custom table to UserProfile
"""

from collections import namedtuple
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from student.models import UserProfile


class Command(BaseCommand):
    """
    Update a userprofile phone field from custom_reg_form_extrainfo table.
    """
    help = 'Update userprofile phone field from custom_reg_form_extrainfo table by country code'

    option_list = BaseCommand.option_list + (
        make_option('--only-active-user',
                    action="store_true",
                    dest='only-active-user',
                    default=False,
                    help='Update phone for only active users',
                    ),
    )

    def handle(self, *args, **options):
       """
       Execute the command
       """
       only_active_user = options.get('only-active-user')
       self.stdout.write("Start to update phone field in User Profile")
       user_profiles_dict = _get_usersprofile_by_country(only_active_user)
       user_id_list = user_profiles_dict.keys()
       result_object = _get_phones_from_users_id(user_id_list)
       self.stdout.write(
           "Start to update phone for {len} users".format(
               len=len(result_object),
           )
       )
       not_valid_value = []
       for result in result_object:
           if len(result.phone) <= UserProfile._meta.get_field('phone').max_length:
               user_profiles_dict[result.user_id].phone = result.phone
               user_profiles_dict[result.user_id].save()
               self.stdout.write(
                   "User id: {user_id}  phone: {phone}".format(user_id=result.user_id, phone=result.phone)
               )
           else:
               not_valid_value.append((
                   "Not updated User with id: {user_id}. "
                   "This phone value not valid: {phone}".format(user_id=result.user_id, phone=result.phone)
               ))
       self.stdout.write("Done")
       if not_valid_value:
           self.stdout.write("Not updated {len} user(s).".format(len=len(not_valid_value)))
           for value in not_valid_value:
               self.stdout.write(value)
               
            
def _get_phones_from_users_id(user_id_list):
    """
    Return a list of namedtuple from custom_reg_form_extrainfo table by user_id
    
    :param user_id_list:  list of a user id
    :return: list of namedtuple
    """
    with connections['default'].cursor() as cursor:
        cursor.execute(
            (
                "SELECT user_id, phone FROM custom_reg_form_extrainfo "
                "WHERE user_id in ({})".format(", ".join([str(i) for i in user_id_list]))
            )
        )
        result_object_list = _namedtuplefetchall(cursor)
    return result_object_list

def _namedtuplefetchall(cursor):
    """
    Return all rows from a cursor as a namedtuple.
    
    :param cursor:  connections cursor
    :return: list of namedtuple
    """
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def _get_usersprofile_by_country(only_active_user):
    """
    Filter and return a dictionary UserProfiles in dictionary.
    
    Dictionary has a user id as key and a UserProfile object as value
    :param only_active_user: True or False
    :return: dictionary
    """
    if only_active_user:
        user_profiles = UserProfile.objects.filter(user__is_active=bool(only_active_user))
    else:
        user_profiles = UserProfile.objects.all()
    user_profiles_dict = {}
    for user_profile in user_profiles:
        user_profiles_dict[user_profile.user.id] = user_profile
    return user_profiles_dict
