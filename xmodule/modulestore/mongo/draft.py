"""
A ModuleStore that knows about a special version DRAFT. Modules
marked as DRAFT are read in preference to modules without the DRAFT
version by this ModuleStore (so, access to i4x://org/course/cat/name
returns the i4x://org/course/cat/name@draft object if that exists,
and otherwise returns i4x://org/course/cat/name).
"""


import logging

from xblock.core import XBlock

from openedx.core.lib.cache_utils import request_cached
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.draft_and_published import DIRECT_ONLY_CATEGORIES, UnsupportedRevisionError
from xmodule.modulestore.exceptions import (
    ItemNotFoundError
)
from xmodule.modulestore.mongo.base import (
    MongoModuleStore,
    MongoRevisionKey,
    as_draft,
)

log = logging.getLogger(__name__)


def wrap_draft(item):
    """
    Cleans the item's location and sets the `is_draft` attribute if needed.

    Sets `item.is_draft` to `True` if the item is DRAFT, and `False` otherwise.
    Sets the item's location to the non-draft location in either case.
    """
    item.is_draft = (item.location.branch == MongoRevisionKey.draft)
    item.location = item.location.replace(revision=MongoRevisionKey.published)
    return item


class DraftModuleStore(MongoModuleStore):
    """
    This mixin modifies a modulestore to give it draft semantics.
    Edits made to units are stored to locations that have the revision DRAFT.
    Reads are first read with revision DRAFT, and then fall back
    to the baseline revision only if DRAFT doesn't exist.

    This module also includes functionality to promote DRAFT modules (and their children)
    to published modules.
    """
    def get_item(self, usage_key, depth=0, revision=None, using_descriptor_system=None, **kwargs):  # lint-amnesty, pylint: disable=arguments-differ
        """
        Returns an XModuleDescriptor instance for the item at usage_key.

        Args:
            usage_key: A :class:`.UsageKey` instance

            depth (int): An argument that some module stores may use to prefetch
                descendants of the queried modules for more efficient results later
                in the request. The depth is counted in the number of calls to
                get_children() to cache.  None indicates to cache all descendants.

            revision:
                ModuleStoreEnum.RevisionOption.published_only - returns only the published item.
                ModuleStoreEnum.RevisionOption.draft_only - returns only the draft item.
                None - uses the branch setting as follows:
                    if branch setting is ModuleStoreEnum.Branch.published_only, returns only the published item.
                    if branch setting is ModuleStoreEnum.Branch.draft_preferred, returns either draft or published item,
                        preferring draft.

                Note: If the item is in DIRECT_ONLY_CATEGORIES, then returns only the PUBLISHED
                version regardless of the revision.

            using_descriptor_system (CachingDescriptorSystem): The existing CachingDescriptorSystem
                to add data to, and to load the XBlocks from.

        Raises:
            xmodule.modulestore.exceptions.InsufficientSpecificationError
            if any segment of the usage_key is None except revision

            xmodule.modulestore.exceptions.ItemNotFoundError if no object
            is found at that usage_key
        """
        def get_published():
            return wrap_draft(super(DraftModuleStore, self).get_item(  # lint-amnesty, pylint: disable=super-with-arguments
                usage_key, depth=depth, using_descriptor_system=using_descriptor_system,
                for_parent=kwargs.get('for_parent'),
            ))

        def get_draft():
            return wrap_draft(super(DraftModuleStore, self).get_item(  # lint-amnesty, pylint: disable=super-with-arguments
                as_draft(usage_key), depth=depth, using_descriptor_system=using_descriptor_system,
                for_parent=kwargs.get('for_parent')
            ))

        # return the published version if ModuleStoreEnum.RevisionOption.published_only is requested
        if revision == ModuleStoreEnum.RevisionOption.published_only:
            return get_published()

        # if the item is direct-only, there can only be a published version
        elif usage_key.block_type in DIRECT_ONLY_CATEGORIES:
            return get_published()

        # return the draft version (without any fallback to PUBLISHED) if DRAFT-ONLY is requested
        elif revision == ModuleStoreEnum.RevisionOption.draft_only:
            return get_draft()

        elif self.get_branch_setting() == ModuleStoreEnum.Branch.published_only:
            return get_published()

        elif revision is None:
            # could use a single query wildcarding revision and sorting by revision. would need to
            # use prefix form of to_deprecated_son
            try:
                # first check for a draft version
                return get_draft()
            except ItemNotFoundError:
                # otherwise, fall back to the published version
                return get_published()

        else:
            raise UnsupportedRevisionError()

    def has_item(self, usage_key, revision=None):  # lint-amnesty, pylint: disable=arguments-differ
        """
        Returns True if location exists in this ModuleStore.

        Args:
            revision:
                ModuleStoreEnum.RevisionOption.published_only - checks for the published item only
                ModuleStoreEnum.RevisionOption.draft_only - checks for the draft item only
                None - uses the branch setting, as follows:
                    if branch setting is ModuleStoreEnum.Branch.published_only, checks for the published item only
                    if branch setting is ModuleStoreEnum.Branch.draft_preferred, checks whether draft or published item exists  # lint-amnesty, pylint: disable=line-too-long
        """
        return False

    def delete_course(self, course_key, user_id):  # lint-amnesty, pylint: disable=arguments-differ
        """
        :param course_key: which course to delete
        :param user_id: id of the user deleting the course
        """
        # Note: does not need to inform the bulk mechanism since after the course is deleted,
        # it can't calculate inheritance anyway. Nothing is there to be dirty.
        # delete the assets
        super().delete_course(course_key, user_id)  # lint-amnesty, pylint: disable=super-with-arguments

        # delete all of the db records for the course
        course_query = self._course_key_to_son(course_key)
        self.collection.delete_many(course_query)
        self.delete_all_asset_metadata(course_key, user_id)

        self._emit_course_deleted_signal(course_key)

    def clone_course(self, source_course_id, dest_course_id, user_id, fields=None, **kwargs):  # lint-amnesty, pylint: disable=unused-argument
        """
        Only called if cloning within this store or if env doesn't set up mixed.
        * copy the courseware
        """
        raise NotImplementedError

    def _clone_modules(self, modules, dest_course_id, user_id):  # lint-amnesty, pylint: disable=unused-argument
        """Clones each module into the given course"""
        raise NotImplementedError

    def _get_raw_parent_locations(self, location, key_revision):  # lint-amnesty, pylint: disable=unused-argument
        """
        Get the parents but don't unset the revision in their locations.

        Intended for internal use but not restricted.

        Args:
            location (UsageKey): assumes the location's revision is None; so, uses revision keyword solely
            key_revision:
                MongoRevisionKey.draft - return only the draft parent
                MongoRevisionKey.published - return only the published parent
                ModuleStoreEnum.RevisionOption.all - return both draft and published parents
        """
        raise NotImplementedError

    def get_parent_location(self, location, revision=None, **kwargs):  # lint-amnesty, pylint: disable=unused-argument
        '''
        Returns the given location's parent location in this course.

        Returns: version agnostic locations (revision always None) as per the rest of mongo.

        Args:
            revision:
                None - uses the branch setting for the revision
                ModuleStoreEnum.RevisionOption.published_only
                    - return only the PUBLISHED parent if it exists, else returns None
                ModuleStoreEnum.RevisionOption.draft_preferred
                    - return either the DRAFT or PUBLISHED parent, preferring DRAFT, if parent(s) exists,
                        else returns None

                    If the draft has a different parent than the published, it returns only
                    the draft's parent. Because parents don't record their children's revisions, this
                    is actually a potentially fragile deduction based on parent type. If the parent type
                    is not DIRECT_ONLY, then the parent revision must be DRAFT.
                    Only xml_exporter currently uses this argument. Others should avoid it.
        '''
        raise NotImplementedError

    def create_xblock(self, runtime, course_key, block_type, block_id=None, fields=None, **kwargs):  # lint-amnesty, pylint: disable=arguments-differ
        """
        Create the new xmodule but don't save it. Returns the new module with a draft locator if
        the category allows drafts. If the category does not allow drafts, just creates a published module.

        :param location: a Location--must have a category
        :param definition_data: can be empty. The initial definition_data for the kvs
        :param metadata: can be empty, the initial metadata for the kvs
        :param runtime: if you already have an xmodule from the course, the xmodule.runtime value
        :param fields: a dictionary of field names and values for the new xmodule
        """
        raise NotImplementedError

    def get_items(self, course_key, revision=None, **kwargs):  # lint-amnesty, pylint: disable=arguments-differ
        """
        Performance Note: This is generally a costly operation, but useful for wildcard searches.

        Returns:
            list of XModuleDescriptor instances for the matching items within the course with
            the given course_key

        NOTE: don't use this to look for courses as the course_key is required. Use get_courses instead.

        Args:
            course_key (CourseKey): the course identifier
            revision:
                ModuleStoreEnum.RevisionOption.published_only - returns only Published items
                ModuleStoreEnum.RevisionOption.draft_only - returns only Draft items
                None - uses the branch setting, as follows:
                    if the branch setting is ModuleStoreEnum.Branch.published_only,
                        returns only Published items
                    if the branch setting is ModuleStoreEnum.Branch.draft_preferred,
                        returns either Draft or Published, preferring Draft items.
        """
        def base_get_items(key_revision):
            return super(DraftModuleStore, self).get_items(course_key, key_revision=key_revision, **kwargs)  # lint-amnesty, pylint: disable=super-with-arguments

        def draft_items():
            return [wrap_draft(item) for item in base_get_items(MongoRevisionKey.draft)]

        def published_items(draft_items):
            # filters out items that are not already in draft_items
            draft_items_locations = {item.location for item in draft_items}
            return [
                item for item in
                base_get_items(MongoRevisionKey.published)
                if item.location not in draft_items_locations
            ]

        if revision == ModuleStoreEnum.RevisionOption.draft_only:
            return draft_items()
        elif revision == ModuleStoreEnum.RevisionOption.published_only \
                or self.get_branch_setting() == ModuleStoreEnum.Branch.published_only:
            return published_items([])
        elif revision is None:
            draft_items = draft_items()
            return draft_items + published_items(draft_items)
        else:
            raise UnsupportedRevisionError()

    def convert_to_draft(self, location, user_id):  # lint-amnesty, pylint: disable=unused-argument
        """
        Copy the subtree rooted at source_location and mark the copies as draft.

        Args:
            location: the location of the source (its revision must be None)
            user_id: the ID of the user doing the operation

        Raises:
            InvalidVersionError: if the source can not be made into a draft
            ItemNotFoundError: if the source does not exist
        """
        raise NotImplementedError

    def _convert_to_draft(self, location, user_id, delete_published=False, ignore_if_draft=False):  # lint-amnesty, pylint: disable=unused-argument
        """
        Internal method with additional internal parameters to convert a subtree to draft.

        Args:
            location: the location of the source (its revision must be MongoRevisionKey.published)
            user_id: the ID of the user doing the operation
            delete_published (Boolean): intended for use by unpublish
            ignore_if_draft(Boolean): for internal use only as part of depth first change

        Raises:
            InvalidVersionError: if the source can not be made into a draft
            ItemNotFoundError: if the source does not exist
            DuplicateItemError: if the source or any of its descendants already has a draft copy. Only
                useful for unpublish b/c we don't want unpublish to overwrite any existing drafts.
        """
        raise NotImplementedError

    def update_item(  # lint-amnesty, pylint: disable=arguments-differ
            self,  # lint-amnesty, pylint: disable=unused-argument
            xblock,
            user_id,
            allow_not_found=False,
            force=False,
            isPublish=False,
            child_update=False,
            **kwargs):
        """
        See superclass doc.
        In addition to the superclass's behavior, this method converts the unit to draft if it's not
        direct-only and not already draft.
        """
        raise NotImplementedError

    def delete_item(self, location, user_id, revision=None, **kwargs):  # lint-amnesty, pylint: disable=arguments-differ
        """
        Delete an item from this modulestore.
        The method determines which revisions to delete. It disconnects and deletes the subtree.
        In general, it assumes deletes only occur on drafts except for direct_only. The only exceptions
        are internal calls like deleting orphans (during publishing as well as from delete_orphan view).
        To indicate that all versions should be deleted, pass the keyword revision=ModuleStoreEnum.RevisionOption.all.

        * Deleting a DIRECT_ONLY_CATEGORIES block, deletes both draft and published children and removes from parent.
        * Deleting a specific version of block whose parent is of DIRECT_ONLY_CATEGORIES, only removes it from parent if
        the other version of the block does not exist. Deletes only children of same version.
        * Other deletions remove from parent of same version and subtree of same version

        Args:
            location: UsageKey of the item to be deleted
            user_id: id of the user deleting the item
            revision:
                None - deletes the item and its subtree, and updates the parents per description above
                ModuleStoreEnum.RevisionOption.published_only - removes only Published versions
                ModuleStoreEnum.RevisionOption.all - removes both Draft and Published parents
                    currently only provided by contentstore.views.item.orphan_handler
                Otherwise, raises a ValueError.
        """
        raise NotImplementedError

    def _delete_subtree(self, location, as_functions, draft_only=False):  # lint-amnesty, pylint: disable=unused-argument
        """
        Internal method for deleting all of the subtree whose revisions match the as_functions
        """
        raise NotImplementedError

    def _breadth_first(self, function, root_usages):  # lint-amnesty, pylint: disable=unused-argument
        """
        Get the root_usage from the db and do a depth first scan. Call the function on each. The
        function should return a list of SON for any next tier items to process and should
        add the SON for any items to delete to the to_be_deleted array.

        At the end, it mass deletes the to_be_deleted items and refreshes the cached metadata inheritance
        tree.

        :param function: a function taking (item, to_be_deleted) and returning [SON] for next_tier invocation
        :param root_usages: the usage keys for the root items (ensure they have the right revision set)
        """
        raise NotImplementedError

    def has_changes(self, xblock):  # lint-amnesty, pylint: disable=unused-argument
        """
        Check if the subtree rooted at xblock has any drafts and thus may possibly have changes
        :param xblock: xblock to check
        :return: True if there are any drafts anywhere in the subtree under xblock (a weaker
            condition than for other stores)
        """
        raise NotImplementedError

    @request_cached(
        # use the XBlock's location value in the cache key
        arg_map_function=lambda arg: str(arg.location if isinstance(arg, XBlock) else arg),
        # use this store's request_cache
        request_cache_getter=lambda args, kwargs: args[1],
    )
    def _cached_has_changes(self, request_cache, xblock):  # lint-amnesty, pylint: disable=unused-argument
        """
        Internal has_changes method that caches the result.
        """
        raise NotImplementedError

    def publish(self, location, user_id, **kwargs):  # lint-amnesty, pylint: disable=unused-argument
        """
        Publish the subtree rooted at location to the live course and remove the drafts.
        Such publishing may cause the deletion of previously published but subsequently deleted
        child trees. Overwrites any existing published xblocks from the subtree.

        Treats the publishing of non-draftable items as merely a subtree selection from
        which to descend.

        Raises:
            ItemNotFoundError: if any of the draft subtree nodes aren't found

        Returns:
            The newly published xblock
        """
        raise NotImplementedError

    def unpublish(self, location, user_id, **kwargs):  # lint-amnesty, pylint: disable=unused-argument
        """
        Turn the published version into a draft, removing the published version.

        NOTE: unlike publish, this gives an error if called above the draftable level as it's intended
        to remove things from the published version
        """
        raise NotImplementedError

    def revert_to_published(self, location, user_id=None):  # lint-amnesty, pylint: disable=unused-argument
        """
        Reverts an item to its last published version (recursively traversing all of its descendants).
        If no published version exists, an InvalidVersionError is thrown.

        If a published version exists but there is no draft version of this item or any of its descendants, this
        method is a no-op. It is also a no-op if the root item is in DIRECT_ONLY_CATEGORIES.

        :raises InvalidVersionError: if no published version exists for the location specified
        """
        raise NotImplementedError

    def update_parent_if_moved(self, original_parent_location, published_version, delete_draft_only, user_id):  # lint-amnesty, pylint: disable=unused-argument
        """
        Update parent of an item if it has moved.

        Arguments:
            original_parent_location (BlockUsageLocator)  : Original parent block locator.
            published_version (dict)   : Published version of the block.
            delete_draft_only (function)    : A callback function to delete draft children if it was moved.
            user_id (int)   : User id
        """
        raise NotImplementedError

    def _query_children_for_cache_children(self, course_key, items):  # lint-amnesty, pylint: disable=unused-argument
        # first get non-draft in a round-trip
        raise NotImplementedError

    def has_published_version(self, xblock):  # lint-amnesty, pylint: disable=unused-argument
        """
        Returns True if this xblock has an existing published version regardless of whether the
        published version is up to date.
        """
        raise NotImplementedError

    def _verify_branch_setting(self, expected_branch_setting):  # lint-amnesty, pylint: disable=unused-argument
        """
        Raises an exception if the current branch setting does not match the expected branch setting.
        """
        raise NotImplementedError
