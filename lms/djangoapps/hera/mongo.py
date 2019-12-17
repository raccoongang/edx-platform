# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from xmodule.mongo_utils import connect_to_mongodb


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

class MongoConnector(Singleton):
    """
    Mongo connector as singleton object to utilize
    mongo connection pool.
    """
    _conn = None

    @property
    def connector(self):
        if not self._conn:
            self._mongo_init()
        return self._conn

    def _mongo_init(self):
        """
        Set class _conn variable.
        """
        options = settings.CONTENTSTORE['DOC_STORE_CONFIG']
        options.pop('collection')  # we just connect to mongo, collection is not needed
        self._conn = connect_to_mongodb(**options)


_conn = MongoConnector()

COURSE_KEY = "course_key"
USER = 'user'
BLOCK_ID = 'block_id'
NEXT_ID = 'next_id'
LEVEL = 'unit_level'



def c_selection_page():
    return _conn.connector['selection_page']
