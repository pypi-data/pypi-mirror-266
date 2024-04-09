"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Sequence, Union

from typing_extensions import Literal

from kelvin.api.client.data_model import DataModelBase

from ..model import requests, responses


class Parameters(DataModelBase):
    @classmethod
    def list_parameters_app_version_asset(
        cls,
        app_name: str,
        version: str,
        asset_name: str,
        search: Optional[Sequence[str]] = None,
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
    ) -> Union[List[responses.ParameterValueItem], responses.ParametersAppVersionAssetListPaginatedResponseCursor]:
        """
        List Asset App Version Parameters lists the app version asset parameters.

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``listParametersAppVersionAsset``: ``GET`` ``/api/v4/parameters/app/{app_name}/versions/{version}/assets/{asset_name}/list``

        Parameters
        ----------
        app_name : :obj:`str`, optional
            A filter on the list based on the key `app_name`. The filter is on the
            full name only. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters.
        version : :obj:`str`, optional
            A filter on the list based on the key `app_version`. The filter is on
            the full value only. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        asset_name : :obj:`str`, optional
            A filter on the list based on the Asset Name in the key `resource`. Do
            not use the `krn` format, only the Asset Name itself. The filter is on
            the full name only. The string can only contain lowercase alphanumeric
            characters and `.`, `_` or `-` characters.
        search : :obj:`Sequence[str]`
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
            Sort the results by one or more enumerators.

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/parameters/app/{app_name}/versions/{version}/assets/{asset_name}/list",
            {"app_name": app_name, "version": version, "asset_name": asset_name},
            {
                "search": search,
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
            {
                "200": responses.ParametersAppVersionAssetListPaginatedResponseCursor,
                "400": None,
                "401": None,
                "404": None,
            },
            False,
            _dry_run,
        )
        return (
            result.fetch("/api/v4/parameters/app/{app_name}/versions/{version}/assets/{asset_name}/list", "GET")
            if fetch and not _dry_run
            else result
        )

    @classmethod
    def update_parameters(
        cls,
        app_name: str,
        version: str,
        asset_name: str,
        data: Optional[Union[requests.ParametersUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Update the value of one or more Parameters in an App.

        **Permission Required:** `kelvin.permission.parameter.update`.

        ``updateParameters``: ``POST`` ``/api/v4/parameters/app/{app_name}/versions/{version}/assets/{asset_name}/update``

        Parameters
        ----------
        app_name : :obj:`str`, optional
            App name in the key `app_name`. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        version : :obj:`str`, optional
            App Version in the key `app_version`.
        asset_name : :obj:`str`, optional
            Asset Name in the key `resource`. Do not use the `krn` format, only
            the Asset Name itself. The string can only contain lowercase
            alphanumeric characters and `.`, `_` or `-` characters.
        data: requests.ParametersUpdate, optional
        **kwargs:
            Extra parameters for requests.ParametersUpdate
              - update_parameters: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/parameters/app/{app_name}/versions/{version}/assets/{asset_name}/update",
            {"app_name": app_name, "version": version, "asset_name": asset_name},
            {},
            {},
            {},
            data,
            "requests.ParametersUpdate",
            False,
            {"200": None, "400": None, "401": None, "404": None},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def get_paramters_app_version_schema(
        cls, app_name: str, version: str, _dry_run: bool = False, _client: Any = None
    ) -> responses.ParamtersAppVersionSchemaGet:
        """
        Get the properties of each Parameter associated with an App.

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``getParamtersAppVersionSchema``: ``GET`` ``/api/v4/parameters/app/{app_name}/versions/{version}/schema/get``

        Parameters
        ----------
        app_name : :obj:`str`, optional
            Parameter key `app_name` to retrieve. The string can only contain
            lowercase alphanumeric characters and `.`, `_` or `-` characters.
        version : :obj:`str`, optional
            Parameter key `app_version` to retireve.

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/parameters/app/{app_name}/versions/{version}/schema/get",
            {"app_name": app_name, "version": version},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.ParamtersAppVersionSchemaGet, "400": None, "401": None, "404": None},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def list_parameters_definitions(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.ParametersDefinitionsList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[List[responses.ParameterDefinitionItem], responses.ParametersDefinitionsListPaginatedResponseCursor]:
        """
        Returns a list of Parameters and its definition in each App. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``listParametersDefinitions``: ``POST`` ``/api/v4/parameters/definitions/list``

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
            Sort the results by one or more enumerators.
        data: requests.ParametersDefinitionsList, optional
        **kwargs:
            Extra parameters for requests.ParametersDefinitionsList
              - list_parameters_definitions: dict

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/parameters/definitions/list",
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
            "requests.ParametersDefinitionsList",
            False,
            {"200": responses.ParametersDefinitionsListPaginatedResponseCursor, "400": None, "401": None, "404": None},
            False,
            _dry_run,
            kwargs,
        )
        return result.fetch("/api/v4/parameters/definitions/list", "POST", data) if fetch and not _dry_run else result

    @classmethod
    def list_parameters_resources(
        cls,
        pagination_type: Optional[Literal["limits", "cursor", "stream"]] = None,
        page_size: Optional[int] = 10000,
        page: Optional[int] = None,
        next: Optional[str] = None,
        previous: Optional[str] = None,
        direction: Optional[Literal["asc", "desc"]] = None,
        sort_by: Optional[Sequence[str]] = None,
        data: Optional[Union[requests.ParametersResourcesList, Mapping[str, Any]]] = None,
        fetch: bool = True,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> Union[List[responses.ParameterValueItem], responses.ParametersResourcesListPaginatedResponseCursor]:
        """
        Returns a list of Parameters and its current value for each Resource. The list can be optionally filtered and sorted on the server before being returned.

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``listParametersResources``: ``POST`` ``/api/v4/parameters/resources/list``

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
            Sort the results by one or more enumerators.
        data: requests.ParametersResourcesList, optional
        **kwargs:
            Extra parameters for requests.ParametersResourcesList
              - list_parameters_resources: dict

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/parameters/resources/list",
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
            "requests.ParametersResourcesList",
            False,
            {"200": responses.ParametersResourcesListPaginatedResponseCursor, "400": None, "401": None, "404": None},
            False,
            _dry_run,
            kwargs,
        )
        return result.fetch("/api/v4/parameters/resources/list", "POST", data) if fetch and not _dry_run else result

    @classmethod
    def get_parameters_values(
        cls,
        data: Optional[Union[requests.ParametersValuesGet, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.ParametersValuesGet:
        """
        Returns a list of all unique values for each Parameter. Default values will not be shown. If the App is not specified, then the response will be grouped by App Name.

        **Permission Required:** `kelvin.permission.parameter.read`.

        ``getParametersValues``: ``POST`` ``/api/v4/parameters/values/get``

        Parameters
        ----------
        data: requests.ParametersValuesGet, optional
        **kwargs:
            Extra parameters for requests.ParametersValuesGet
              - get_parameters_values: dict

        """

        from ..model import responses

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/parameters/values/get",
            {},
            {},
            {},
            {},
            data,
            "requests.ParametersValuesGet",
            False,
            {"200": responses.ParametersValuesGet, "400": None, "401": None, "404": None},
            False,
            _dry_run,
            kwargs,
        )
        return result
