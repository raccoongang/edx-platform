import re
import requests
from django.conf import settings


def to_snakecase(s):
    """A helper for converting a string to camel_case"""
    return s.lower().replace(' ', '_')


class ZohoRecord:
    """A convenience class to access a Zoho row by attribute names"""
    def __init__(self, zoho_row):
        try:
            print(zoho_row)
            self.dict = {to_snakecase(field['val']): field['content']
                         for field in zoho_row['FL'] if field != 'no'}
        except TypeError:
            print('failed to process row:', zoho_row)
            raise

    def __getattr__(self, attrname):
        return self.dict.get(attrname, '')

    def __str__(self):
        fields = ', '.join('%s="%s"' % kv for kv in self.dict.items())
        return 'ZohoRecord(%s)' % fields


def fetch_all_zoho_records(endpoint, params):
    """Exhaustively fetches from the Zoho API
    Returns ZohoRecord objects for each matching record
    """
    records = []
    while True:
        
        response_dict = requests.get(endpoint, params).json()
        if 'result' not in response_dict['response']:
            break
        student_list = response_dict['response']['result']['Contacts']['row']
        for row in student_list:
            records.append(ZohoRecord(row))

        params['fromIndex'] += settings.ZOHO_RESPONSE_SIZE
        params['toIndex'] += settings.ZOHO_RESPONSE_SIZE
    
    return records


def get_students(status):
    """Fetch from Zoho all emails for contacts with *Onboarding* status"""
    endpoint = settings.ZOHO_ENDPOINT_PREFIX + '/Contacts/searchRecords'
    params = {
        'authtoken': settings.ZOHO_TOKEN,
        'scope': 'crmapi',
        'criteria': status,
        'fromIndex': 1,
        'toIndex': settings.ZOHO_RESPONSE_SIZE,
    }
    return fetch_all_zoho_records(endpoint, params)


def parse_course_of_interest_code(course_of_interest_code):
    """
    Course codes in Zoho are created based on the following criteria:

    <year_and_month><course_identifier>-<course_location>

    For example, a course of interest code of 1708FS-ON translates to:
    17 -> the year (2017)
    08 -> the month (August)
    FS -> Fullstack
    ON -> Online

    We need to strip away the excess and focus on the course identifier,
    in this case `FS`

    `course_of_interest_code` is the code that's retrieved from the
        student's Zoho record
    
    Returns the course_identifier without the year/month/location
    """
    regex_matcher = "\d|\-.*$"
    course_code = re.sub(regex_matcher, '', course_of_interest_code)
    return 'FS' if course_code == 'SBFS' else course_code


def update_student_record(zap_url, student_email):
    """
    Update the Zoho record for a student to indicate their new status
    within the LMS.

    `student_email` is the email of the student that is to be updated
    """

    params = {
        'student_email': student_email
    }
    response = requests.post(zap_url, data=params)