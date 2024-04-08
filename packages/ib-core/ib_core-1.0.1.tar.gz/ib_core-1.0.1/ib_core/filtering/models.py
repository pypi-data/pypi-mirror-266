from typing import Literal

from django.db.models import Q

from ib_core.filtering.types import operators, OR, AND
from ib_core.mixins.authorization import AuthorizationReader
from ib_core.models import Tag
from ib_core.tags.manage import get_tags_by_value


class Filter:
    """
    A model for configuring tag filtering parameters

    Used only for the 'filter' method of the TagManager model,
    using outside doesn't make sense.
    """

    ######################
    # in the development #
    ######################
    filter_operator: operators
    key: str
    values: list[str]
    auth: AuthorizationReader

    def __init__(self, key, *values, operator: operators = OR):
        self.key = key
        self.values = [value for value in values]
        self.filter_operator = operator

    def set_auth(self, auth: AuthorizationReader):
        self.auth = auth

    def get_tags_by_values(self) -> dict[str: str]:
        tags = {}
        for value in self.values:
            try:
                tags[value] = [tag.get("id") for tag in get_tags_by_value(value, self.auth)]
            except Exception as ex: # noqa
                pass
        return tags

    def to_query(self):
        tags = self.get_tags_by_values()
        return [Q(key=self.key, tag=value) for key, value in tags.items()]
