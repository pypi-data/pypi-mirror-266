from typing import Optional, Union

import antimatter.client as openapi_client
from antimatter.tags import TagType


class WriteContextRegexRuleBuilder:
    """
    Builder class for creating a WriteContextRegexRule
    """

    def __init__(self, pattern: str, match_on_key: bool = False):
        """
        Initialize a new instance of WriteContextRegexRuleBuilder.

        :param pattern: The regex pattern for matching
        :param match_on_key: If True, match against the key instead of the field
        """
        self._pattern = pattern
        self._match_on_key = match_on_key
        self._span_tags = []
        self._capsule_tags = []

    def add_span_tag(
        self,
        name: str,
        tag_type: Union[str, TagType] = TagType.Unary,
        value: Optional[str] = None,
    ) -> 'WriteContextRegexRuleBuilder':
        """
        The span tag to add when the regex rule matches

        :param name: The span tag name
        :param tag_type: The span tag type; default 'unary'
        :param value: The span tag value, if the tag_type is not 'unary'
        :return: The builder instance
        """
        tag_type = TagType(tag_type).name.lower()
        self._span_tags.append(openapi_client.WriteContextRegexTag(
            name=name, value=value, type=openapi_client.TagTypeField(tag_type),
        ))
        return self

    def add_capsule_tag(
        self,
        name: str,
        tag_type: Union[str, TagType] = TagType.Unary,
        value: Optional[str] = None,
    ) -> 'WriteContextRegexRuleBuilder':
        """
        The capsule tag to add when the regex rule matches

        :param name: The capsule tag name
        :param tag_type: The capsule tag type; default 'unary'
        :param value: The capsule tag value, if the tag_type is not 'unary'
        :return: The builder instance
        """
        tag_type = TagType(tag_type).name.lower()
        self._capsule_tags.append(openapi_client.WriteContextRegexTag(
            name=name, value=value, type=openapi_client.TagTypeField(tag_type),
        ))
        return self

    def build(self) -> openapi_client.WriteContextRegexRule:
        """
        Build the rule.

        :return: The built rule
        """
        return openapi_client.WriteContextRegexRule(
            pattern=self._pattern,
            match_on_key=self._match_on_key,
            span_tags=self._span_tags,
            capsule_tags=self._capsule_tags,
        )
