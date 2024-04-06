from datetime import datetime
from typing import Any, Callable, Dict, Iterator, List, Optional

import antimatter.client as openapi_client
from antimatter.tags import CapsuleTag
from antimatter.cap_prep.applicator import TAG_SOURCE, TAG_VERSION
from antimatter.client import DefaultApi
from antimatter.session_mixins.token import exec_with_token


class CapsuleMixin:
    """
    Session mixin defining CRUD functionality for capsules and tags.
    """

    _page_res_size: int = 100

    def __init__(self, domain: str, client_func: Callable[[], DefaultApi], **kwargs):
        try:
            super().__init__(domain=domain, client_func=client_func, **kwargs)
        except TypeError:
            super().__init__()  # If this is last mixin, super() will be object()
        self._domain = domain
        self._client_func = client_func

    @exec_with_token
    def list_capsules(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        span_tag: Optional[str] = None,
        sort_on: Optional[str] = None,
        ascending: Optional[bool] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Returns an iterator over the capsules available for the current domain and auth

        :param start_date: The earlier date of the date range. As results are returned in reverse chronological order, this date corresponds with the end of the result set.
        :param end_date: The later date of the date range. As results are returned in reverse chronological order, this date corresponds with the beginning of the result set. If not specified, defaults to the current time.
        :param span_tag: The span tag you would like to filter on. This accepts a tag key only and will return all span tag key results matching the provided tag key. If not specified, this field is ignored.
        :param sort_on: The capsule field you would like to sort on. This accepts the field only and will return results ordered on the provided field. If not specified, this field is ignored.
        :param ascending: This defines whether a sorted result should be order ascending. This accepts a boolean value and when true will work in combination with the sort_on and start_after parameters to return values in ascending order. If not specified, this field is ignored and treated as false.
        """
        pagination = None
        while True:
            res = self._client_func().domain_list_capsules(
                domain_id=self._domain,
                start_date=start_date,
                end_date=end_date,
                num_results=self._page_res_size,
                span_tags=span_tag,
                sort_on=sort_on,
                start_after=pagination,
                ascending=ascending,
            )
            if not res.results:
                break
            for capsule in res.results:
                pagination = capsule.page_key
                yield capsule.model_dump(exclude={"page_key"})

    @exec_with_token
    def get_capsule_info(self, capsule_id: str) -> Dict[str, Any]:
        """
        Get the summary information about the capsule.

        :param capsule_id: The identifier for the capsule
        :return: The summary information about the capsule
        """
        return self._client_func().domain_get_capsule_info(
            domain_id=self._domain, capsule_id=capsule_id,
        ).model_dump()

    @exec_with_token
    def upsert_capsule_tags(self, capsule_id: str, tags: List[CapsuleTag]) -> None:
        """
        Upsert the capsule-level tags to apply to a capsule.

        :param capsule_id: The capsule to apply tags to
        :param tags: The tags to apply to the capsule
        """
        self._client_func().domain_upsert_capsule_tags(
            domain_id=self._domain, capsule_id=capsule_id, tag=[
                openapi_client.Tag(
                    name=tag.name,
                    value=tag.tag_value,
                    type=tag.tag_type.name.lower(),
                    hook_version=f"{TAG_VERSION[0]}.{TAG_VERSION[1]}.{TAG_VERSION[2]}",
                    source=TAG_SOURCE,
                ) for tag in tags
            ]
        )

    @exec_with_token
    def delete_capsule_tags(self, capsule_id: str, tag_names: List[str]) -> None:
        """
        Delete capsule-level tags

        :param capsule_id: The capsule to delete tags from
        :param tag_names: The names of the tags to delete
        """
        self._client_func().domain_delete_capsule_tags(
            domain_id=self._domain,
            capsule_id=capsule_id,
            delete_tags=openapi_client.DeleteTags(names=tag_names),
        )
