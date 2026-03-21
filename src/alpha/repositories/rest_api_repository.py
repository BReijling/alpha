"""This module contains the the `RestApiRepository` class."""

from urllib.parse import urlencode, urljoin
from uuid import UUID

import requests
from requests.cookies import cookiejar_from_dict  # type: ignore
from requests.models import Response
from typing import Any, Generic, TypeVar

from alpha.domain.models.base_model import BaseDomainModel, DomainModel
from alpha.infra.models.json_patch import JsonPatch

MODEL = TypeVar("MODEL", bound=BaseDomainModel)


class RestApiRepository(Generic[DomainModel]):
    """Implementation of `ApiRepository` that interacts with a RESTful API
    using the `requests` library.

    This repository provides methods for common CRUD operations (Create, Read,
    Update, Delete). It handles the construction of API URLs, serialization/
    deserialization of domain models, and interaction with the `requests`
    library. It also allows for flexible configuration of the API endpoints,
    session management, and response handling. The repository can be easily
    extended or customized for specific API requirements.

    Parameters
    ----------
    Generic
        The type of the domain model that this repository will manage. This
        allows for type safety and better integration with the rest of the
        application.
    """

    def __init__(
        self,
        host: str,
        scheme: str | None = None,
        base_path: str = "",
        endpoint: str = "",
        default_model: DomainModel | None = None,
        use_factory: bool = True,
        serialize: bool = True,
        model_factory_method_name: str = "from_dict",
        model_serialization_method_name: str = "to_dict",
        session: requests.sessions.Session | None = None,
        request_headers: dict[str, str] | None = None,
        request_cookies: dict[str, str] | None = None,
        request_timeout: int | None = 30,
        response_data_attribute: str | None = None,
    ) -> None:
        """Initialize the REST API repository.

        Parameters
        ----------
        host
            The base URL of the API.
        scheme, optional
            The URL scheme to use (e.g., "http" or "https"). This is only used
            if the host does not already include a scheme, by default "https"
        base_path, optional
            The base path of the API, by default ""
        endpoint, optional
            The default endpoint for the API. This value is used when no
            specific endpoint is provided in the method calls, by default ""
        default_model, optional
            The default model to use for serialization/deserialization,
            by default None
        use_factory, optional
            Whether to use the model factory method for creating models from
            response data, by default True
        serialize, optional
            Whether to serialize objects before sending them in requests,
            by default True
        model_factory_method_name, optional
            The name of the class method to use for creating models from
            dictionaries, by default "from_dict"
        model_serialization_method_name, optional
            The name of the method to use for serializing models to
            dictionaries, by default "to_dict"
        session, optional
            The requests session to use, by default None
        request_headers, optional
            Default headers to include in every request, by default None
        request_timeout, optional
            The timeout for API requests in seconds, by default 30
        response_data_attribute, optional
            The attribute in the response data to extract the relevant data
            from, by default None
        """
        self._host = host
        self._scheme = scheme or "https"
        self._base_path = base_path
        self._endpoint = endpoint
        self._default_model = default_model
        self._use_factory = use_factory
        self._serialize = serialize
        self._model_factory_method_name = model_factory_method_name
        self._model_serialization_method_name = model_serialization_method_name
        self._session = session or requests.sessions.Session()
        self._request_headers = request_headers or {}
        self._request_cookies = request_cookies or {}
        self._request_timeout = request_timeout
        self._response_data_attribute = response_data_attribute

        # Update session with default headers and cookies
        self._session.headers.update(request_headers or {})
        cookiejar_from_dict(
            request_cookies or {},
            cookiejar=self._session.cookies,
            overwrite=True,
        )

    def add(
        self,
        obj: DomainModel,
        return_obj: bool = True,
        serialize: bool | None = None,
        use_factory: bool | None = None,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        model: DomainModel | None = None,
        additional_request_params: dict[str, Any] | None = None,
        **params: Any,
    ) -> DomainModel | dict[str, Any] | None:
        """Add a new resource.

        Parameters
        ----------
        obj
            The object to add.
        return_obj
            Whether to return the added object or not.
        serialize
            Whether to serialize the object before sending it in the API
            request.
        use_factory
            Whether to use the model factory method for creating models from
            response data.
        endpoint
            The API endpoint to which the object should be added.
        parent_endpoint
            The parent API endpoint, if the resource is nested under a parent
            resource.
        parent_param
            The parameter to identify the parent resource, if applicable. This
            could be an ID or a unique identifier. The parameter will be
            appended to the parent endpoint to form the full URL for the API
            request.
        model
            The model to use for serialization/deserialization.
        additional_request_params
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.
        **params
            Additional query parameters to include in the API request.

        Returns
        -------
            The added object if `return_obj` is `True`, otherwise `None`.
        """
        if self._determine_serialization(serialize):
            obj = self._serialize_object(obj)

        url = self._build_url(
            endpoint,
            parent_endpoint=parent_endpoint,
            parent_param=parent_param,
            **params,
        )

        object = self._post(
            url=url,
            data=obj,
            additional_request_params=additional_request_params,
        )

        if return_obj is False:
            return None

        if not self._determine_use_factory(use_factory):
            return object

        return self._map_object(object, model)

    def add_all(
        self,
        objs: list[DomainModel],
        return_objs: bool = True,
        serialize: bool | None = None,
        use_factory: bool | None = None,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        model: DomainModel | None = None,
        additional_request_params: dict[str, Any] | None = None,
        one_by_one: bool = False,
        **params: Any,
    ) -> list[DomainModel] | list[dict[str, Any]] | None:
        """Add multiple new resources.

        Parameters
        ----------
        objs
            The objects to add.
        return_obj
            Whether to return the added object or not.
        serialize
            Whether to serialize the object before sending it in the API
            request.
        use_factory
            Whether to use the model factory method for creating models from
            response data.
        endpoint
            The API endpoint to which the object should be added.
        parent_endpoint
            The parent API endpoint, if the resource is nested under a parent
            resource.
        parent_param
            The parameter to identify the parent resource, if applicable. This
            could be an ID or a unique identifier. The parameter will be
            appended to the parent endpoint to form the full URL for the API
            request.
        model
            The model to use for serialization/deserialization.
        additional_request_params
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.
        one_by_one
            Whether to add the objects one by one (i.e. make a separate API
            call for each object).
        **params
            Additional query parameters to include in the API request.

        Returns
        -------
            The added objects if `return_obj` is `True`, otherwise `None`.
        """
        if one_by_one:
            results: list[DomainModel] | list[dict[str, Any]] = []
            for obj in objs:
                result = self.add(
                    obj=obj,
                    return_obj=return_objs,
                    serialize=serialize,
                    use_factory=use_factory,
                    endpoint=endpoint,
                    parent_endpoint=parent_endpoint,
                    parent_param=parent_param,
                    model=model,
                    additional_request_params=additional_request_params,
                    **params,
                )
                if result:
                    results.append(result)  # type: ignore
            return results if return_objs else None

        if self._determine_serialization(serialize):
            objs = [self._serialize_object(obj) for obj in objs]

        url = self._build_url(
            endpoint,
            parent_endpoint=parent_endpoint,
            parent_param=parent_param,
            **params,
        )

        response = self._post(
            url=url,
            data=objs,
            additional_request_params=additional_request_params,
        )

        if return_objs is False:
            return None

        if not self._determine_use_factory(use_factory):
            return response

        return self._map_array(response, model)

    def get(
        self,
        use_factory: bool | None = None,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        param: str | None = None,
        model: DomainModel | None = None,
        additional_request_params: dict[str, Any] | None = None,
        **params: Any,
    ) -> DomainModel | dict[str, Any]:
        """Retrieve a single resource.

        Parameters
        ----------
        endpoint
            The API endpoint from which to retrieve the resource.
        use_factory
            Whether to use the model factory method for creating models from
            response data.
        endpoint
            The API endpoint to which the object should be added.
        parent_endpoint
            The parent API endpoint, if the resource is nested under a parent
            resource.
        parent_param
            The parameter to identify the parent resource, if applicable. This
            could be an ID or a unique identifier. The parameter will be
            appended to the parent endpoint to form the full URL for the API
            request.
        param
            The parameter to identify the specific resource. This could be an
            ID or a unique identifier. The parameter will be appended to the
            endpoint to form the full URL for the GET request.
        model
            The model to use for serialization/deserialization.
        additional_request_params
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.
        **params
            Additional query parameters to include in the API request.

        Returns
        -------
            The retrieved object.
        """
        url = self._build_url(
            endpoint,
            parent_endpoint=parent_endpoint,
            parent_param=parent_param,
            param=param,
            **params,
        )

        object = self._get(
            url=url,
            additional_request_params=additional_request_params,
        )

        if not self._determine_use_factory(use_factory):
            return object

        return self._map_object(object, model)

    def get_all(
        self,
        use_factory: bool | None = None,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        param: str | None = None,
        model: DomainModel | None = None,
        additional_request_params: dict[str, Any] | None = None,
        **params: Any,
    ) -> list[DomainModel] | list[dict[str, Any]]:
        """Retrieve multiple resources.

        Parameters
        ----------
        endpoint
            The API endpoint from which to retrieve the resource.
        use_factory
            Whether to use the model factory method for creating models from
            response data.
        endpoint
            The API endpoint to which the object should be added.
        parent_endpoint
            The parent API endpoint, if the resource is nested under a parent
            resource.
        parent_param
            The parameter to identify the parent resource, if applicable. This
            could be an ID or a unique identifier. The parameter will be
            appended to the parent endpoint to form the full URL for the API
            request.
        param
            The parameter to identify the specific resource. This could be an
            ID or a unique identifier. The parameter will be appended to the
            endpoint to form the full URL for the GET request.
        model
            The model to use for serialization/deserialization.
        additional_request_params
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.
        **params
            Additional query parameters to include in the API request.

        Returns
        -------
            The retrieved objects.
        """
        objects = self.get(
            use_factory=False,
            endpoint=endpoint,
            parent_endpoint=parent_endpoint,
            parent_param=parent_param,
            param=param,
            model=model,
            additional_request_params=additional_request_params,
            **params,
        )

        if not self._determine_use_factory(use_factory):
            return objects

        return self._map_array(objects, model)

    def patch(
        self,
        patch: JsonPatch,
        return_obj: bool = True,
        use_factory: bool | None = None,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        param: str | None = None,
        model: DomainModel | None = None,
        additional_request_params: dict[str, Any] | None = None,
        **params: Any,
    ) -> DomainModel | dict[str, Any] | None:
        """Update a resource.

        Parameters
        ----------
        patch
            The JSON Patch object containing the changes to be applied to the
            resource.
        return_obj
            Whether to return the updated object or not.
        use_factory
            Whether to use the model factory method for creating models from
            response data.
        endpoint
            The API endpoint to which the object should be added.
        parent_endpoint
            The parent API endpoint, if the resource is nested under a parent
            resource.
        parent_param
            The parameter to identify the parent resource, if applicable. This
            could be an ID or a unique identifier. The parameter will be
            appended to the parent endpoint to form the full URL for the API
            request.
        param
            The parameter to identify the specific resource. This could be an
            ID or a unique identifier. The parameter will be appended to the
            endpoint to form the full URL for the GET request.
        model
            The model to use for serialization/deserialization.
        additional_request_params
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.
        **params
            Additional query parameters to include in the API request.

        Returns
        -------
            The updated object if `return_obj` is `True`, otherwise `None`.
        """
        url = self._build_url(
            endpoint,
            parent_endpoint=parent_endpoint,
            parent_param=parent_param,
            param=param,
            **params,
        )

        object = self._patch(
            url=url,
            patch=patch,
            additional_request_params=additional_request_params,
        )

        if return_obj is False:
            return None

        if not self._determine_use_factory(use_factory):
            return object

        return self._map_object(object, model)

    def remove(
        self,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        param: str | None = None,
        additional_request_params: dict[str, Any] | None = None,
        **params: Any,
    ) -> None:
        """Remove a resource.

        Parameters
        ----------
        endpoint
            The API endpoint to which the object should be added.
        parent_endpoint
            The parent API endpoint, if the resource is nested under a parent
            resource.
        parent_param
            The parameter to identify the parent resource, if applicable. This
            could be an ID or a unique identifier. The parameter will be
            appended to the parent endpoint to form the full URL for the API
            request.
        param
            The parameter to identify the specific resource. This could be an
            ID or a unique identifier. The parameter will be appended to the
            endpoint to form the full URL for the GET request.
        additional_request_params
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.
        **params
            Additional query parameters to include in the API request.
        """
        url = self._build_url(
            endpoint,
            parent_endpoint=parent_endpoint,
            parent_param=parent_param,
            param=param,
            **params,
        )

        self._delete(
            url=url,
            additional_request_params=additional_request_params,
        )

    def update(
        self,
        obj: DomainModel,
        return_obj: bool,
        serialize: bool | None = None,
        use_factory: bool | None = None,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        param: str | None = None,
        model: DomainModel | None = None,
        additional_request_params: dict[str, Any] | None = None,
        **params: Any,
    ) -> DomainModel | dict[str, Any] | None:
        """Update a resource.

        Parameters
        ----------
        obj
            The object to add.
        return_obj
            Whether to return the added object or not.
        serialize
            Whether to serialize the object before sending it in the API
            request.
        use_factory
            Whether to use the model factory method for creating models from
            response data.
        endpoint
            The API endpoint to which the object should be added.
        parent_endpoint
            The parent API endpoint, if the resource is nested under a parent
            resource.
        parent_param
            The parameter to identify the parent resource, if applicable. This
            could be an ID or a unique identifier. The parameter will be
            appended to the parent endpoint to form the full URL for the API
            request.
        param
            The parameter to identify the specific resource. This could be an
            ID or a unique identifier. The parameter will be appended to the
            endpoint to form the full URL for the GET request.
        model
            The model to use for serialization/deserialization.
        additional_request_params
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.
        **params
            Additional query parameters to include in the API request.

        Returns
        -------
            The updated object if `return_obj` is `True`, otherwise `None`.
        """
        if self._determine_serialization(serialize):
            obj = self._serialize_object(obj)

        url = self._build_url(
            endpoint,
            parent_endpoint=parent_endpoint,
            parent_param=parent_param,
            param=param,
            **params,
        )

        object = self._put(
            url=url,
            data=obj,
            additional_request_params=additional_request_params,
        )

        if return_obj is False:
            return None

        if not self._determine_use_factory(use_factory):
            return object

        return self._map_object(object, model)

    def _get(
        self,
        url: str,
        additional_request_params: dict[str, Any] | None = None,
    ) -> Any:
        """Call the GET method of the API.

        Parameters
        ----------
        url
            A fully constructed URL to which the GET request should be sent.
            This URL should include any necessary query parameters. The URL is
            expected to be properly formatted and ready for use in an API
            request.
        additional_request_params, optional
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.

        Returns
        -------
            The data retrieved from the API response.
        """
        response = self._session.get(
            url=url,
            timeout=self._request_timeout,
            **(additional_request_params or {}),
        )

        if response.status_code == 200:
            return self._get_data_from_response(response)
        else:
            response.raise_for_status()

    def _post(
        self,
        url: str,
        data: Any,
        additional_request_params: dict[str, Any] | None = None,
    ) -> Any:
        """Call the POST method of the API.

        Parameters
        ----------
        url
            A fully constructed URL to which the POST request should be sent.
            This URL should include any necessary query parameters. The URL is
            expected to be properly formatted and ready for use in an API
            request.
        data
            The data to be sent in the body of the POST request. This data is
            expected to be in a format that can be serialized to JSON, as it
            will be sent as JSON in the request body.
        additional_request_params, optional
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.

        Returns
        -------
            The data retrieved from the API response.
        """
        response = self._session.post(
            url=url,
            json=data,
            timeout=self._request_timeout,
            **(additional_request_params or {}),
        )

        if response.status_code in (200, 201):
            return self._get_data_from_response(response)
        else:
            response.raise_for_status()

    def _patch(
        self,
        url: str,
        patch: JsonPatch,
        additional_request_params: dict[str, Any] | None = None,
    ) -> Any:
        """Call the PATCH method of the API.

        Parameters
        ----------
        url
            A fully constructed URL to which the PATCH request should be sent.
            This URL should include any necessary query parameters. The URL is
            expected to be properly formatted and ready for use in an API
            request.
        patch
            The JSON Patch object containing the changes to be applied to the
            resource. This object should conform to the JSON Patch
            specification.
        additional_request_params, optional
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.

        Returns
        -------
            The data retrieved from the API response.
        """
        response = self._session.patch(
            url=url,
            json=patch,
            timeout=self._request_timeout,
            **(additional_request_params or {}),
        )

        if response.status_code == 200:
            return self._get_data_from_response(response)
        else:
            response.raise_for_status()

    def _put(
        self,
        url: str,
        data: Any,
        additional_request_params: dict[str, Any] | None = None,
    ) -> Any:
        """Call the PUT method of the API.

        Parameters
        ----------
        url
            A fully constructed URL to which the PUT request should be sent.
            This URL should include any necessary query parameters. The URL is
            expected to be properly formatted and ready for use in an API
            request.
        data
            The data to be sent in the body of the PUT request. This data is
            expected to be in a format that can be serialized to JSON, as it
            will be sent as JSON in the request body.
        additional_request_params, optional
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.

        Returns
        -------
            The data retrieved from the API response.
        """
        response = self._session.put(
            url=url,
            json=data,
            timeout=self._request_timeout,
            **(additional_request_params or {}),
        )

        if response.status_code == 200:
            return self._get_data_from_response(response)
        else:
            response.raise_for_status()

    def _delete(
        self, url: str, additional_request_params: dict[str, Any] | None = None
    ) -> None:
        """_summary_

        Parameters
        ----------
        url
            A fully constructed URL to which the DELETE request should be sent.
            This URL should include any necessary query parameters. The URL is
            expected to be properly formatted and ready for use in an API
            request.
        additional_request_params, optional
            Additional parameters to include in the function call which handles
            the API request. This allows for flexibility in specifying
            parameters such as headers, authentication tokens, or other request
            options that may be needed for the API call.
        """
        response = self._session.delete(
            url=url,
            timeout=self._request_timeout,
            **(additional_request_params or {}),
        )

        if response.status_code != 204:
            response.raise_for_status()

    def _map_object(self, response: Any, model: MODEL | None) -> MODEL:
        """Map a single object from the API response to a model instance.

        Parameters
        ----------
        response
            The API response containing the data to be mapped.
        model
            The model class to which the data should be mapped. If None, the
            default model for the repository will be used.

        Returns
        -------
            An instance of the model populated with the data from the API
            response.
        """
        model_to_use = model or self._default_model

        return getattr(model_to_use, self._model_factory_method_name)(response)

    def _map_array(
        self, response: list[Any], model: MODEL | None
    ) -> list[MODEL]:
        """Map an array of objects from the API response to model instances.

        Parameters
        ----------
        response
            The API response containing the data to be mapped.
        model
            The model class to which the data should be mapped. If None, the
            default model for the repository will be used.

        Returns
        -------
            A list of model instances populated with the data from the API
            response.
        """
        model_to_use = model or self._default_model

        return [
            getattr(model_to_use, self._model_factory_method_name)(item)
            for item in response
        ]

    def _build_url(
        self,
        endpoint: str | None = None,
        param: str | int | UUID | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        **params: Any,
    ) -> str:
        """Build an URL to use for HTTP requests.

        The method constructs the URL based on the provided endpoint and
        parameter, as well as the base host, scheme, and base path configured
        for the repository. The endpoint and parameter are optional, allowing
        for flexible URL construction. The method ensures that the URL is
        properly formatted and can be used for making API requests.

        The method detects if the scheme is provided and constructs the URL
        accordingly. If a scheme is provided, it will be included in the URL.
        If not, the URL will be constructed without a scheme, allowing for
        relative URLs or URLs with a different scheme. If the scheme is already
        included in the host, it will not be replaced.

        An optional parent endpoint and parameter can be included in the URL,
        which is useful for nested resources. The parent parameter will be
        appended after the parent endpoint, and the main parameter will be
        appended after the main endpoint.

        Parameters
        ----------
        endpoint, optional
            The endpoint to use for the URL, by default None
        param, optional
            The parameter to append to the URL, by default None
        parent_endpoint, optional
            An optional parent endpoint to include in the URL, by default None
        parent_param, optional
            An optional parameter to append after the parent endpoint,
            by default None
        **params
            Additional parameters that can be used for query parameters.

        Returns
        -------
            The constructed URL as a string
        """
        if self._scheme and not self._host.__contains__("://"):
            url = f"{self._scheme}://{self._host}"
        else:
            url = self._host

        endpoint = endpoint or self._endpoint

        if self._base_path:
            url = urljoin(url, self._base_path.strip("/") + "/")

        if parent_endpoint:
            url = urljoin(url, parent_endpoint.lstrip("/"))

        if parent_param is not None:
            url = urljoin(url + "/", str(parent_param))

        if endpoint:
            url = urljoin(url + "/", endpoint.lstrip("/"))

        if param:
            url = urljoin(url + "/", str(param))

        if params:
            url = url + "?" + urlencode(params, doseq=True)

        return url

    def _serialize_object(self, obj: Any) -> Any:
        """Serialize an object using the specified serialization method if it
        exists.

        Parameters
        ----------
        obj
            The object to be serialized.

        Returns
        -------
            The serialized object if the serialization method exists, otherwise
            the original object.
        """
        if hasattr(obj, self._model_serialization_method_name):
            return getattr(obj, self._model_serialization_method_name)()
        return obj

    def _get_data_from_response(self, response: Response) -> Any:
        """Extract data from the API response. If the response_data_attribute
        is configured, it will return the value of that attribute. Otherwise,
        it will return the entire response data.

        Parameters
        ----------
        response
            The API response object.

        Returns
        -------
            The extracted data from the API response.
        """
        data = response.json()
        if self._response_data_attribute:
            return data.get(self._response_data_attribute)
        return data

    def _determine_serialization(
        self,
        serialize: bool | None,
    ) -> bool:
        """Determine to use the serialize variable or self._serialize for
        deciding whether to serialize the object before sending it in the API
        request.

        Parameters
        ----------
        serialize
            Whether to serialize the object before sending it in the API
            request.

        Returns
        -------
            The value to use for deciding whether to serialize the object before
            sending it in the API request.
        """
        return serialize if serialize is not None else self._serialize

    def _determine_use_factory(
        self,
        use_factory: bool | None,
    ) -> bool:
        """Determine to use the use_factory variable or self._use_factory for
        deciding whether to use the model factory method for creating models.

        Parameters
        ----------
        use_factory
            Whether to use the model factory method for creating models from
            response data.

        Returns
        -------
            The value to use for deciding whether to use the model factory
            method for creating models from response data.
        """
        return use_factory if use_factory is not None else self._use_factory
