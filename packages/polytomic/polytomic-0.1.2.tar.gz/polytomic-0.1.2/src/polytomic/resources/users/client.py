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
from ...types.api_key_response_envelope import ApiKeyResponseEnvelope
from ...types.list_users_envelope import ListUsersEnvelope
from ...types.rest_err_response import RestErrResponse
from ...types.user_envelope import UserEnvelope

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class UsersClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def list(self, org_id: str, *, request_options: typing.Optional[RequestOptions] = None) -> ListUsersEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - org_id: str.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.users.list(
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"api/organizations/{jsonable_encoder(org_id)}/users"
            ),
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
            return pydantic.parse_obj_as(ListUsersEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def create(
        self,
        org_id: str,
        *,
        email: str,
        role: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> UserEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - org_id: str.

            - email: str.

            - role: typing.Optional[str].

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.users.create(
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
            email="mail@example.com",
            role="admin",
        )
        """
        _request: typing.Dict[str, typing.Any] = {"email": email}
        if role is not OMIT:
            _request["role"] = role
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"api/organizations/{jsonable_encoder(org_id)}/users"
            ),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
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
            return pydantic.parse_obj_as(UserEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def get(self, id: str, org_id: str, *, request_options: typing.Optional[RequestOptions] = None) -> UserEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - id: str.

            - org_id: str.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.users.get(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"api/organizations/{jsonable_encoder(org_id)}/users/{jsonable_encoder(id)}",
            ),
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
            return pydantic.parse_obj_as(UserEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def remove(self, id: str, org_id: str, *, request_options: typing.Optional[RequestOptions] = None) -> UserEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - id: str.

            - org_id: str.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.users.remove(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "DELETE",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"api/organizations/{jsonable_encoder(org_id)}/users/{jsonable_encoder(id)}",
            ),
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
            return pydantic.parse_obj_as(UserEnvelope, _response.json())  # type: ignore
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
        org_id: str,
        *,
        email: str,
        role: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> UserEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - id: str.

            - org_id: str.

            - email: str.

            - role: typing.Optional[str].

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.users.update(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
            email="mail@example.com",
            role="admin",
        )
        """
        _request: typing.Dict[str, typing.Any] = {"email": email}
        if role is not OMIT:
            _request["role"] = role
        _response = self._client_wrapper.httpx_client.request(
            "PATCH",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"api/organizations/{jsonable_encoder(org_id)}/users/{jsonable_encoder(id)}",
            ),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
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
            return pydantic.parse_obj_as(UserEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def create_api_key(
        self,
        org_id: str,
        id: str,
        *,
        force: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ApiKeyResponseEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - org_id: str.

            - id: str.

            - force: typing.Optional[bool].

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import Polytomic

        client = Polytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        client.users.create_api_key(
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
            force=True,
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"api/organizations/{jsonable_encoder(org_id)}/users/{jsonable_encoder(id)}/keys",
            ),
            params=jsonable_encoder(
                remove_none_from_dict(
                    {
                        "force": force,
                        **(
                            request_options.get("additional_query_parameters", {})
                            if request_options is not None
                            else {}
                        ),
                    }
                )
            ),
            json=jsonable_encoder(remove_none_from_dict(request_options.get("additional_body_parameters", {})))
            if request_options is not None
            else None,
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
            return pydantic.parse_obj_as(ApiKeyResponseEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncUsersClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def list(self, org_id: str, *, request_options: typing.Optional[RequestOptions] = None) -> ListUsersEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - org_id: str.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.users.list(
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"api/organizations/{jsonable_encoder(org_id)}/users"
            ),
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
            return pydantic.parse_obj_as(ListUsersEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def create(
        self,
        org_id: str,
        *,
        email: str,
        role: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> UserEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - org_id: str.

            - email: str.

            - role: typing.Optional[str].

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.users.create(
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
            email="mail@example.com",
            role="admin",
        )
        """
        _request: typing.Dict[str, typing.Any] = {"email": email}
        if role is not OMIT:
            _request["role"] = role
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"api/organizations/{jsonable_encoder(org_id)}/users"
            ),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
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
            return pydantic.parse_obj_as(UserEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def get(
        self, id: str, org_id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> UserEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - id: str.

            - org_id: str.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.users.get(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"api/organizations/{jsonable_encoder(org_id)}/users/{jsonable_encoder(id)}",
            ),
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
            return pydantic.parse_obj_as(UserEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def remove(
        self, id: str, org_id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> UserEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - id: str.

            - org_id: str.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.users.remove(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "DELETE",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"api/organizations/{jsonable_encoder(org_id)}/users/{jsonable_encoder(id)}",
            ),
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
            return pydantic.parse_obj_as(UserEnvelope, _response.json())  # type: ignore
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
        org_id: str,
        *,
        email: str,
        role: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> UserEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - id: str.

            - org_id: str.

            - email: str.

            - role: typing.Optional[str].

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.users.update(
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
            email="mail@example.com",
            role="admin",
        )
        """
        _request: typing.Dict[str, typing.Any] = {"email": email}
        if role is not OMIT:
            _request["role"] = role
        _response = await self._client_wrapper.httpx_client.request(
            "PATCH",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"api/organizations/{jsonable_encoder(org_id)}/users/{jsonable_encoder(id)}",
            ),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
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
            return pydantic.parse_obj_as(UserEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def create_api_key(
        self,
        org_id: str,
        id: str,
        *,
        force: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ApiKeyResponseEnvelope:
        """
        > 🚧 Requires partner key
        >
        > User endpoints are only accessible using [partner keys](https://docs.polytomic.com/reference/authentication#partner-keys)

        Parameters:
            - org_id: str.

            - id: str.

            - force: typing.Optional[bool].

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from polytomic.client import AsyncPolytomic

        client = AsyncPolytomic(
            x_polytomic_version="YOUR_X_POLYTOMIC_VERSION",
            token="YOUR_TOKEN",
        )
        await client.users.create_api_key(
            org_id="248df4b7-aa70-47b8-a036-33ac447e668d",
            id="248df4b7-aa70-47b8-a036-33ac447e668d",
            force=True,
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"api/organizations/{jsonable_encoder(org_id)}/users/{jsonable_encoder(id)}/keys",
            ),
            params=jsonable_encoder(
                remove_none_from_dict(
                    {
                        "force": force,
                        **(
                            request_options.get("additional_query_parameters", {})
                            if request_options is not None
                            else {}
                        ),
                    }
                )
            ),
            json=jsonable_encoder(remove_none_from_dict(request_options.get("additional_body_parameters", {})))
            if request_options is not None
            else None,
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
            return pydantic.parse_obj_as(ApiKeyResponseEnvelope, _response.json())  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(RestErrResponse, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
