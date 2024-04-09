"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Sequence, Union

from typing_extensions import Literal

from kelvin.api.client.data_model import DataModelBase

from ..model import requests, responses, type


class DataTag(DataModelBase):
    @classmethod
    def create_data_tag(
        cls,
        data: Optional[Union[requests.DataTagCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataTagCreate:
        """
        Create a new Data Tag event.

        **Permission Required:** `kelvin.permission.data_tag.create`.

        ``createDataTag``: ``POST`` ``/api/v4/datatags/create``

        Parameters
        ----------
        data: requests.DataTagCreate, optional
        **kwargs:
            Extra parameters for requests.DataTagCreate
              - create_data_tag: dict

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/create",
            {},
            {},
            {},
            {},
            data,
            "requests.DataTagCreate",
            False,
            {"201": responses.DataTagCreate, "400": None, "401": None, "409": None},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_data_tags(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.DataTagsList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[List[type.DataTag], responses.DataTagsListPaginatedResponseCursor]:
        """
        Returns a list of Data Tags. The Data Tags can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.data_tag.read`.

        ``listDataTags``: ``POST`` ``/api/v4/datatags/list``

        Parameters
        ----------
        pagination_type : :obj:`Literal['limits', 'cursor', 'stream']`
            Method of pagination to use for return results where `total_items` is
            greater than `page_size`. `cursor` and `limits` will return one `page`
            of results, `stream` will return all results. ('limits', 'cursor',
            'stream')
        page_size : :obj:`int`
            Number of objects to be returned in each page. Page size can range
            between 1 and 1000 objects.
        page : :obj:`int`
            An integer for the wanted page of results. Used only with
            `pagination_type` set as `limits`.
        next : :obj:`str`
            An alphanumeric string bookmark to indicate where to start for the
            next page. Used only with `pagination_type` set as `cursor`.
        previous : :obj:`str`
            An alphanumeric string bookmark to indicate where to end for the
            previous page. Used only with `pagination_type` set as `cursor`.
        direction : :obj:`Literal['asc', 'desc']`
            Sorting order according to the `sort_by` parameter. ('asc', 'desc')
        sort_by : :obj:`Sequence[str]`
        data: requests.DataTagsList, optional
        **kwargs:
            Extra parameters for requests.DataTagsList
              - list_data_tags: dict

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/list",
            {},
            {
                "pagination_type": pagination_type,
                "page_size": page_size,
                "page": page,
                "next": next,
                "previous": previous,
                "direction": direction,
                "sort_by": sort_by,
            },
            {},
            {},
            data,
            "requests.DataTagsList",
            False,
            {"200": responses.DataTagsListPaginatedResponseCursor, "400": None, "401": None},
            False,
            _dry_run,
            kwargs,
        )
        return result.fetch("/api/v4/datatags/list", "POST", data) if fetch and not _dry_run else result

    @classmethod
    def create_tag(
        cls,
        data: Optional[Union[requests.TagCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.TagCreate:
        """
        Create a new Tag.

        **Permission Required:** `kelvin.permission.data_tag.create`.

        ``createTag``: ``POST`` ``/api/v4/datatags/tags/create``

        Parameters
        ----------
        data: requests.TagCreate, optional
        **kwargs:
            Extra parameters for requests.TagCreate
              - create_tag: dict

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/tags/create",
            {},
            {},
            {},
            {},
            data,
            "requests.TagCreate",
            False,
            {"201": responses.TagCreate, "400": None, "401": None, "409": None},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_tags(
        cls,
        search: Optional[Sequence[str]] = None,
        names: Optional[Sequence[str]] = None,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> Union[List[type.Tag], responses.TagsListPaginatedResponseCursor]:
        """
        Returns a list of Tags. The Tags can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.data_tag.read`.

        ``listTags``: ``GET`` ``/api/v4/datatags/tags/list``

        Parameters
        ----------
        search : :obj:`Sequence[str]`
            Search and filter on the list based on the key `name` (Tag Name). All
            values in array will be filtered as `OR`. The search is case
            insensitive and will find partial matches as well.
        names : :obj:`Sequence[str]`
            Filter on the list based on the key `name` (Tag Name). All values in
            array will be filtered as `OR`. The search is case insensitive and is
            on the full Tags `name` only.
        pagination_type : :obj:`Literal['limits', 'cursor', 'stream']`
            Method of pagination to use for return results where `total_items` is
            greater than `page_size`. `cursor` and `limits` will return one `page`
            of results, `stream` will return all results. ('limits', 'cursor',
            'stream')
        page_size : :obj:`int`
            Number of objects to be returned in each page. Page size can range
            between 1 and 1000 objects.
        page : :obj:`int`
            An integer for the wanted page of results. Used only with
            `pagination_type` set as `limits`.
        next : :obj:`str`
            An alphanumeric string bookmark to indicate where to start for the
            next page. Used only with `pagination_type` set as `cursor`.
        previous : :obj:`str`
            An alphanumeric string bookmark to indicate where to end for the
            previous page. Used only with `pagination_type` set as `cursor`.
        direction : :obj:`Literal['asc', 'desc']`
            Sorting order according to the `sort_by` parameter. ('asc', 'desc')
        sort_by : :obj:`Sequence[str]`

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datatags/tags/list",
            {},
            {
                "search": search,
                "names": names,
                "pagination_type": pagination_type,
                "page_size": page_size,
                "page": page,
                "next": next,
                "previous": previous,
                "direction": direction,
                "sort_by": sort_by,
            },
            {},
            {},
            None,
            None,
            False,
            {"200": responses.TagsListPaginatedResponseCursor, "400": None, "401": None},
            False,
            _dry_run,
        )
        return result.fetch("/api/v4/datatags/tags/list", "GET") if fetch and not _dry_run else result

    @classmethod
    def delete_tag(cls, tag_name: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Tag. An error will be returned if there are any current links to a DataTag and the Tag will not be deleted.
        **Permission Required:** `kelvin.permission.data_tag.delete`.

        ``deleteTag``: ``POST`` ``/api/v4/datatags/tags/{tag_name}/delete``

        Parameters
        ----------
        tag_name : :obj:`str`, optional
            Tag key `name`.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/tags/{tag_name}/delete",
            {"tag_name": tag_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": None, "400": None, "401": None, "404": None},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_tag(cls, tag_name: str, _dry_run: bool = False, _client: Any = None) -> responses.TagGet:
        """
        Retrieves a Tag.

        **Permission Required:** `kelvin.permission.data_tag.read`.

        ``getTag``: ``GET`` ``/api/v4/datatags/tags/{tag_name}/get``

        Parameters
        ----------
        tag_name : :obj:`str`, optional
            Tag key `name`.

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datatags/tags/{tag_name}/get",
            {"tag_name": tag_name},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.TagGet, "400": None, "404": None},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_tag(
        cls,
        tag_name: str,
        data: Optional[Union[requests.TagUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.TagUpdate:
        """
        Update an existing Tag. The Tag key `name` can not be updated.

        **Permission Required:** `kelvin.permission.data_tag.update`.

        ``updateTag``: ``POST`` ``/api/v4/datatags/tags/{tag_name}/update``

        Parameters
        ----------
        tag_name : :obj:`str`, optional
            Tag key `name`.
        data: requests.TagUpdate, optional
        **kwargs:
            Extra parameters for requests.TagUpdate
              - update_tag: dict

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/tags/{tag_name}/update",
            {"tag_name": tag_name},
            {},
            {},
            {},
            data,
            "requests.TagUpdate",
            False,
            {"200": responses.TagUpdate, "400": None, "401": None, "404": None},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_data_tag(cls, datatag_id: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Permanently delete an existing Data Tag.
        **Permission Required:** `kelvin.permission.data_tag.delete`.

        ``deleteDataTag``: ``POST`` ``/api/v4/datatags/{datatag_id}/delete``

        Parameters
        ----------
        datatag_id : :obj:`str`, optional
            Data Tag key `id`. The string can only contain alphanumeric characters
            and `-` character.

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/{datatag_id}/delete",
            {"datatag_id": datatag_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": None, "400": None, "401": None, "404": None},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_data_tag(cls, datatag_id: str, _dry_run: bool = False, _client: Any = None) -> responses.DataTagGet:
        """
        Retrieves a Data Tag.

        **Permission Required:** `kelvin.permission.data_tag.read`.

        ``getDataTag``: ``GET`` ``/api/v4/datatags/{datatag_id}/get``

        Parameters
        ----------
        datatag_id : :obj:`str`, optional
            Data Tag key `id`. The string can only contain alphanumeric characters
            and `-` character.

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/datatags/{datatag_id}/get",
            {"datatag_id": datatag_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.DataTagGet, "400": None, "404": None},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_data_tag(
        cls,
        datatag_id: str,
        data: Optional[Union[requests.DataTagUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.DataTagUpdate:
        """
        Update an existing Data Tag. Any parameters that are not provided will remain unchanged.

        **Permission Required:** `kelvin.permission.data_tag.update`.

        ``updateDataTag``: ``POST`` ``/api/v4/datatags/{datatag_id}/update``

        Parameters
        ----------
        datatag_id : :obj:`str`, optional
            Data Tag key `id`. The string can only contain alphanumeric characters
            and `-` character.
        data: requests.DataTagUpdate, optional
        **kwargs:
            Extra parameters for requests.DataTagUpdate
              - update_data_tag: dict

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/datatags/{datatag_id}/update",
            {"datatag_id": datatag_id},
            {},
            {},
            {},
            data,
            "requests.DataTagUpdate",
            False,
            {"200": responses.DataTagUpdate, "400": None, "401": None, "404": None},
            False,
            _dry_run,
            kwargs,
        )
        return result
