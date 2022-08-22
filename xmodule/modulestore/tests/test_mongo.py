"""
Unit tests for the Mongo modulestore
"""


import logging

import pytest

# pylint: disable=protected-access
from django.test import TestCase
# pylint: enable=E0611
from opaque_keys.edx.keys import CourseKey
from xblock.exceptions import InvalidScopeError
from xblock.fields import Scope
from xblock.runtime import KeyValueStore

from xmodule.modulestore.mongo import MongoKeyValueStore

log = logging.getLogger(__name__)


class TestMongoKeyValueStore(TestCase):
    """
    Tests for MongoKeyValueStore.
    """

    def setUp(self):
        super().setUp()
        self.data = {'foo': 'foo_value'}
        self.course_id = CourseKey.from_string('org/course/run')
        self.parent = self.course_id.make_usage_key('parent', 'p')
        self.children = [self.course_id.make_usage_key('child', 'a'), self.course_id.make_usage_key('child', 'b')]
        self.metadata = {'meta': 'meta_val'}
        self.kvs = MongoKeyValueStore(self.data, self.parent, self.children, self.metadata)

    def test_read(self):
        assert self.kvs.get(KeyValueStore.Key(Scope.content, None, None, 'foo')) == self.data['foo']
        assert self.kvs.get(KeyValueStore.Key(Scope.parent, None, None, 'parent')) == self.parent
        assert self.kvs.get(KeyValueStore.Key(Scope.children, None, None, 'children')) == self.children
        assert self.kvs.get(KeyValueStore.Key(Scope.settings, None, None, 'meta')) == self.metadata['meta']

    def test_read_invalid_scope(self):
        for scope in (Scope.preferences, Scope.user_info, Scope.user_state):
            key = KeyValueStore.Key(scope, None, None, 'foo')
            with pytest.raises(InvalidScopeError):
                self.kvs.get(key)
            assert not self.kvs.has(key)

    def test_read_non_dict_data(self):
        self.kvs = MongoKeyValueStore('xml_data', self.parent, self.children, self.metadata)
        assert self.kvs.get(KeyValueStore.Key(Scope.content, None, None, 'data')) == 'xml_data'

    def _check_write(self, key, value):
        self.kvs.set(key, value)
        assert self.kvs.get(key) == value

    def test_write(self):
        yield (self._check_write, KeyValueStore.Key(Scope.content, None, None, 'foo'), 'new_data')
        yield (self._check_write, KeyValueStore.Key(Scope.children, None, None, 'children'), [])
        yield (self._check_write, KeyValueStore.Key(Scope.children, None, None, 'parent'), None)
        yield (self._check_write, KeyValueStore.Key(Scope.settings, None, None, 'meta'), 'new_settings')

    def test_write_non_dict_data(self):
        self.kvs = MongoKeyValueStore('xml_data', self.parent, self.children, self.metadata)
        self._check_write(KeyValueStore.Key(Scope.content, None, None, 'data'), 'new_data')

    def test_write_invalid_scope(self):
        for scope in (Scope.preferences, Scope.user_info, Scope.user_state):
            with pytest.raises(InvalidScopeError):
                self.kvs.set(KeyValueStore.Key(scope, None, None, 'foo'), 'new_value')

    def _check_delete_default(self, key, default_value):
        self.kvs.delete(key)
        assert self.kvs.get(key) == default_value
        assert self.kvs.has(key)

    def _check_delete_key_error(self, key):
        self.kvs.delete(key)
        with pytest.raises(KeyError):
            self.kvs.get(key)
        assert not self.kvs.has(key)

    def test_delete(self):
        yield (self._check_delete_key_error, KeyValueStore.Key(Scope.content, None, None, 'foo'))
        yield (self._check_delete_default, KeyValueStore.Key(Scope.children, None, None, 'children'), [])
        yield (self._check_delete_key_error, KeyValueStore.Key(Scope.settings, None, None, 'meta'))

    def test_delete_invalid_scope(self):
        for scope in (Scope.preferences, Scope.user_info, Scope.user_state, Scope.parent):
            with pytest.raises(InvalidScopeError):
                self.kvs.delete(KeyValueStore.Key(scope, None, None, 'foo'))
