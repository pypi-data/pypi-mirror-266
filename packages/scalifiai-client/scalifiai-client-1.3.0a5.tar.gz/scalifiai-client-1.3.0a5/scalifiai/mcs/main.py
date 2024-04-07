from scalifiai.base import BaseModule, Table
from .constants import URL_SLUG
from .exceptions import (
    MCSSubModuleTagsProxyDictInvalidOperationValueException,
    MCSSubModuleTagsProxyDictInvalidOperationException,
    MCSSubModuleTagsProxyDictNotFoundException,
    MCSSubModuleTagsProxyDictMultipleTagsDeleteExceptionException,
)


class MCS(BaseModule):
    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    module_url_slug = URL_SLUG


class MCSSubModuleTagsProxyDict(dict):

    def __init__(self, *args, parent_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_instance = parent_instance

    def __setitem__(self, __key, __value) -> None:

        return self.parent_instance.attach_tags(tags=[{"key": __key, "value": __value}])

    def _getitem_internal(self, *, key=None):

        if isinstance(key, str) != True:
            raise MCSSubModuleTagsProxyDictInvalidOperationValueException()

        list_tags_data = self.parent_instance._list_tags(
            extra_query_params={"key__exact": key}
        )
        tags_queryset = list_tags_data["results"]

        if len(tags_queryset) > 1:

            table_instance = Table(
                data=tags_queryset, local_timezone=self.parent_instance.local_timezone
            )

            return table_instance.to_representation(
                default_columns=list_tags_data["default_visible_columns"]["cli"],
                columns=None,
                column_mapping=self.parent_instance.tags_verbose_column_mapping,
                verbose_columns=True,
            )
        elif len(tags_queryset) == 1:
            return tags_queryset[0]
        elif len(tags_queryset) == 0:
            raise MCSSubModuleTagsProxyDictNotFoundException()

    def __getitem__(self, __key):

        if isinstance(__key, str) != True:
            raise MCSSubModuleTagsProxyDictInvalidOperationValueException()

        tag_data = self._getitem_internal(key=__key)
        if isinstance(tag_data, dict):
            return tag_data["value"]

        return tag_data

    def __repr__(self):
        return repr(self.parent_instance.list_tags())

    def __delitem__(self, __key) -> None:

        tag_data = self._getitem_internal(key=__key)
        if isinstance(tag_data, dict):
            return self.parent_instance.remove_tag(tag_id=tag_data["id"])

        raise MCSSubModuleTagsProxyDictMultipleTagsDeleteExceptionException()

    def popitem(self) -> tuple:
        raise MCSSubModuleTagsProxyDictInvalidOperationException()

    def pop(self, __key):
        return self.__delitem__(__key)

    def clear(self):
        return self.parent_instance.remove_all_tags()

    def items(self):
        raise MCSSubModuleTagsProxyDictInvalidOperationException()

    # TODO[VIMPORTANT] ALSO HANDLE OTHER METHODS LIKE .keys(), .values()
