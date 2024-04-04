# This file was auto-generated from our API Definition.

import typing
import urllib.parse
from json.decoder import JSONDecodeError

from ...core.api_error import ApiError
from ...core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ...core.jsonable_encoder import jsonable_encoder
from ...core.remove_none_from_dict import remove_none_from_dict
from ...core.request_options import RequestOptions
from ...errors.unauthorized_error import UnauthorizedError
from ...types.model_list_response_envelope import ModelListResponseEnvelope
from ...types.model_model_field_request import ModelModelFieldRequest
from ...types.model_relation import ModelRelation
from ...types.model_response_envelope import ModelResponseEnvelope
from ...types.rest_err_response import RestErrResponse

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class ModelsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def list(self, *, request_options: typing.Optional[RequestOptions] = None) -> ModelListResponseEnvelope:
        """
        Parameters:
            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.models.list()
        """
        _response = self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "api/models"),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(ModelListResponseEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def create(
        self,
        *,
        async_: typing.Optional[bool] = None,
        additional_fields: typing.Optional[typing.Sequence[ModelModelFieldRequest]] = OMIT,
        configuration: typing.Optional[typing.Dict[str, typing.Any]] = OMIT,
        connection_id: str,
        fields: typing.Optional[typing.Sequence[str]] = OMIT,
        identifier: typing.Optional[str] = OMIT,
        labels: typing.Optional[typing.Sequence[str]] = OMIT,
        name: str,
        organization_id: typing.Optional[str] = OMIT,
        policies: typing.Optional[typing.Sequence[str]] = OMIT,
        relations: typing.Optional[typing.Sequence[ModelRelation]] = OMIT,
        tracking_columns: typing.Optional[typing.Sequence[str]] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ModelResponseEnvelope:
        """
        Parameters:
            - async_: typing.Optional[bool].

            - additional_fields: typing.Optional[typing.Sequence[ModelModelFieldRequest]].

            - configuration: typing.Optional[typing.Dict[str, typing.Any]].

            - connection_id: str.

            - fields: typing.Optional[typing.Sequence[str]].

            - identifier: typing.Optional[str].

            - labels: typing.Optional[typing.Sequence[str]].

            - name: str.

            - organization_id: typing.Optional[str].

            - policies: typing.Optional[typing.Sequence[str]].

            - relations: typing.Optional[typing.Sequence[ModelRelation]].

            - tracking_columns: typing.Optional[typing.Sequence[str]].

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.models.create(
            connection_id="248df4b7-aa70-47b8-a036-33ac447e668d",
            identifier="id",
            name="Users",
        )
        """
        _request: typing.Dict[str, typing.Any] = {"connection_id": connection_id, "name": name}
        if additional_fields is not OMIT:
            _request["additional_fields"] = additional_fields
        if configuration is not OMIT:
            _request["configuration"] = configuration
        if fields is not OMIT:
            _request["fields"] = fields
        if identifier is not OMIT:
            _request["identifier"] = identifier
        if labels is not OMIT:
            _request["labels"] = labels
        if organization_id is not OMIT:
            _request["organization_id"] = organization_id
        if policies is not OMIT:
            _request["policies"] = policies
        if relations is not OMIT:
            _request["relations"] = relations
        if tracking_columns is not OMIT:
            _request["tracking_columns"] = tracking_columns
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "api/models"),
            params=jsonable_encoder(
                remove_none_from_dict(
                    {
                        "async": async_,
                        **(
                            request_options.get("additional_query_parameters", {})
                            if request_options is not None
                            else {}
                        ),
                    }
                )
            ),
            json=jsonable_encoder(_request)
            if request_options is None or request_options.get("additional_body_parameters") is None
            else {
                **jsonable_encoder(_request),
                **(jsonable_encoder(remove_none_from_dict(request_options.get("additional_body_parameters", {})))),
            },
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(ModelResponseEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def get(self, id: str, *, request_options: typing.Optional[RequestOptions] = None) -> ModelResponseEnvelope:
        """
        Parameters:
            - id: str.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.models.get(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", f"api/models/{jsonable_encoder(id)}"),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(ModelResponseEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def remove(self, id: str, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """
        Parameters:
            - id: str.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.models.remove(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "DELETE",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", f"api/models/{jsonable_encoder(id)}"),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def update(
        self,
        id: str,
        *,
        async_: typing.Optional[bool] = None,
        additional_fields: typing.Optional[typing.Sequence[ModelModelFieldRequest]] = OMIT,
        configuration: typing.Optional[typing.Dict[str, typing.Any]] = OMIT,
        connection_id: str,
        fields: typing.Optional[typing.Sequence[str]] = OMIT,
        identifier: typing.Optional[str] = OMIT,
        labels: typing.Optional[typing.Sequence[str]] = OMIT,
        name: str,
        organization_id: typing.Optional[str] = OMIT,
        policies: typing.Optional[typing.Sequence[str]] = OMIT,
        relations: typing.Optional[typing.Sequence[ModelRelation]] = OMIT,
        tracking_columns: typing.Optional[typing.Sequence[str]] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ModelResponseEnvelope:
        """
        Parameters:
            - id: str.

            - async_: typing.Optional[bool].

            - additional_fields: typing.Optional[typing.Sequence[ModelModelFieldRequest]].

            - configuration: typing.Optional[typing.Dict[str, typing.Any]].

            - connection_id: str.

            - fields: typing.Optional[typing.Sequence[str]].

            - identifier: typing.Optional[str].

            - labels: typing.Optional[typing.Sequence[str]].

            - name: str.

            - organization_id: typing.Optional[str].

            - policies: typing.Optional[typing.Sequence[str]].

            - relations: typing.Optional[typing.Sequence[ModelRelation]].

            - tracking_columns: typing.Optional[typing.Sequence[str]].

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.models.update(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
            async_=False,
            connection_id="248df4b7-aa70-47b8-a036-33ac447e668d",
            identifier="id",
            name="Users",
        )
        """
        _request: typing.Dict[str, typing.Any] = {"connection_id": connection_id, "name": name}
        if additional_fields is not OMIT:
            _request["additional_fields"] = additional_fields
        if configuration is not OMIT:
            _request["configuration"] = configuration
        if fields is not OMIT:
            _request["fields"] = fields
        if identifier is not OMIT:
            _request["identifier"] = identifier
        if labels is not OMIT:
            _request["labels"] = labels
        if organization_id is not OMIT:
            _request["organization_id"] = organization_id
        if policies is not OMIT:
            _request["policies"] = policies
        if relations is not OMIT:
            _request["relations"] = relations
        if tracking_columns is not OMIT:
            _request["tracking_columns"] = tracking_columns
        _response = self._client_wrapper.httpx_client.request(
            "PATCH",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", f"api/models/{jsonable_encoder(id)}"),
            params=jsonable_encoder(
                remove_none_from_dict(
                    {
                        "async": async_,
                        **(
                            request_options.get("additional_query_parameters", {})
                            if request_options is not None
                            else {}
                        ),
                    }
                )
            ),
            json=jsonable_encoder(_request)
            if request_options is None or request_options.get("additional_body_parameters") is None
            else {
                **jsonable_encoder(_request),
                **(jsonable_encoder(remove_none_from_dict(request_options.get("additional_body_parameters", {})))),
            },
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(ModelResponseEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncModelsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def list(self, *, request_options: typing.Optional[RequestOptions] = None) -> ModelListResponseEnvelope:
        """
        Parameters:
            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.models.list()
        """
        _response = await self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "api/models"),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(ModelListResponseEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def create(
        self,
        *,
        async_: typing.Optional[bool] = None,
        additional_fields: typing.Optional[typing.Sequence[ModelModelFieldRequest]] = OMIT,
        configuration: typing.Optional[typing.Dict[str, typing.Any]] = OMIT,
        connection_id: str,
        fields: typing.Optional[typing.Sequence[str]] = OMIT,
        identifier: typing.Optional[str] = OMIT,
        labels: typing.Optional[typing.Sequence[str]] = OMIT,
        name: str,
        organization_id: typing.Optional[str] = OMIT,
        policies: typing.Optional[typing.Sequence[str]] = OMIT,
        relations: typing.Optional[typing.Sequence[ModelRelation]] = OMIT,
        tracking_columns: typing.Optional[typing.Sequence[str]] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ModelResponseEnvelope:
        """
        Parameters:
            - async_: typing.Optional[bool].

            - additional_fields: typing.Optional[typing.Sequence[ModelModelFieldRequest]].

            - configuration: typing.Optional[typing.Dict[str, typing.Any]].

            - connection_id: str.

            - fields: typing.Optional[typing.Sequence[str]].

            - identifier: typing.Optional[str].

            - labels: typing.Optional[typing.Sequence[str]].

            - name: str.

            - organization_id: typing.Optional[str].

            - policies: typing.Optional[typing.Sequence[str]].

            - relations: typing.Optional[typing.Sequence[ModelRelation]].

            - tracking_columns: typing.Optional[typing.Sequence[str]].

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.models.create(
            connection_id="248df4b7-aa70-47b8-a036-33ac447e668d",
            identifier="id",
            name="Users",
        )
        """
        _request: typing.Dict[str, typing.Any] = {"connection_id": connection_id, "name": name}
        if additional_fields is not OMIT:
            _request["additional_fields"] = additional_fields
        if configuration is not OMIT:
            _request["configuration"] = configuration
        if fields is not OMIT:
            _request["fields"] = fields
        if identifier is not OMIT:
            _request["identifier"] = identifier
        if labels is not OMIT:
            _request["labels"] = labels
        if organization_id is not OMIT:
            _request["organization_id"] = organization_id
        if policies is not OMIT:
            _request["policies"] = policies
        if relations is not OMIT:
            _request["relations"] = relations
        if tracking_columns is not OMIT:
            _request["tracking_columns"] = tracking_columns
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "api/models"),
            params=jsonable_encoder(
                remove_none_from_dict(
                    {
                        "async": async_,
                        **(
                            request_options.get("additional_query_parameters", {})
                            if request_options is not None
                            else {}
                        ),
                    }
                )
            ),
            json=jsonable_encoder(_request)
            if request_options is None or request_options.get("additional_body_parameters") is None
            else {
                **jsonable_encoder(_request),
                **(jsonable_encoder(remove_none_from_dict(request_options.get("additional_body_parameters", {})))),
            },
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(ModelResponseEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def get(self, id: str, *, request_options: typing.Optional[RequestOptions] = None) -> ModelResponseEnvelope:
        """
        Parameters:
            - id: str.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.models.get(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", f"api/models/{jsonable_encoder(id)}"),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(ModelResponseEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def remove(self, id: str, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """
        Parameters:
            - id: str.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.models.remove(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "DELETE",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", f"api/models/{jsonable_encoder(id)}"),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def update(
        self,
        id: str,
        *,
        async_: typing.Optional[bool] = None,
        additional_fields: typing.Optional[typing.Sequence[ModelModelFieldRequest]] = OMIT,
        configuration: typing.Optional[typing.Dict[str, typing.Any]] = OMIT,
        connection_id: str,
        fields: typing.Optional[typing.Sequence[str]] = OMIT,
        identifier: typing.Optional[str] = OMIT,
        labels: typing.Optional[typing.Sequence[str]] = OMIT,
        name: str,
        organization_id: typing.Optional[str] = OMIT,
        policies: typing.Optional[typing.Sequence[str]] = OMIT,
        relations: typing.Optional[typing.Sequence[ModelRelation]] = OMIT,
        tracking_columns: typing.Optional[typing.Sequence[str]] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ModelResponseEnvelope:
        """
        Parameters:
            - id: str.

            - async_: typing.Optional[bool].

            - additional_fields: typing.Optional[typing.Sequence[ModelModelFieldRequest]].

            - configuration: typing.Optional[typing.Dict[str, typing.Any]].

            - connection_id: str.

            - fields: typing.Optional[typing.Sequence[str]].

            - identifier: typing.Optional[str].

            - labels: typing.Optional[typing.Sequence[str]].

            - name: str.

            - organization_id: typing.Optional[str].

            - policies: typing.Optional[typing.Sequence[str]].

            - relations: typing.Optional[typing.Sequence[ModelRelation]].

            - tracking_columns: typing.Optional[typing.Sequence[str]].

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.models.update(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
            async_=False,
            connection_id="248df4b7-aa70-47b8-a036-33ac447e668d",
            identifier="id",
            name="Users",
        )
        """
        _request: typing.Dict[str, typing.Any] = {"connection_id": connection_id, "name": name}
        if additional_fields is not OMIT:
            _request["additional_fields"] = additional_fields
        if configuration is not OMIT:
            _request["configuration"] = configuration
        if fields is not OMIT:
            _request["fields"] = fields
        if identifier is not OMIT:
            _request["identifier"] = identifier
        if labels is not OMIT:
            _request["labels"] = labels
        if organization_id is not OMIT:
            _request["organization_id"] = organization_id
        if policies is not OMIT:
            _request["policies"] = policies
        if relations is not OMIT:
            _request["relations"] = relations
        if tracking_columns is not OMIT:
            _request["tracking_columns"] = tracking_columns
        _response = await self._client_wrapper.httpx_client.request(
            "PATCH",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", f"api/models/{jsonable_encoder(id)}"),
            params=jsonable_encoder(
                remove_none_from_dict(
                    {
                        "async": async_,
                        **(
                            request_options.get("additional_query_parameters", {})
                            if request_options is not None
                            else {}
                        ),
                    }
                )
            ),
            json=jsonable_encoder(_request)
            if request_options is None or request_options.get("additional_body_parameters") is None
            else {
                **jsonable_encoder(_request),
                **(jsonable_encoder(remove_none_from_dict(request_options.get("additional_body_parameters", {})))),
            },
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(ModelResponseEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
