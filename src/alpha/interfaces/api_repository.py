"""Interfaces for HTTP/API-backed repository implementations."""

from typing import Any, Literal, Protocol, overload, runtime_checkable
from uuid import UUID

from alpha.domain.models.base_model import DomainModel
from alpha.infra.models.json_patch import JsonPatch


@runtime_checkable
class ApiRepository(Protocol[DomainModel]):
    """Repository contract for remote API resources."""

    @overload
    def add(
        self,
        obj: DomainModel,
        return_obj: Literal[True],
        serialize: bool | None,
        use_factory: Literal[True, None],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> DomainModel: ...

    @overload
    def add(
        self,
        obj: DomainModel,
        return_obj: Literal[True],
        serialize: bool | None,
        use_factory: Literal[False],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> dict[str, Any]: ...

    @overload
    def add(
        self,
        obj: DomainModel,
        return_obj: Literal[False],
        serialize: bool | None,
        use_factory: bool | None,
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> None: ...

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
        DomainModel | dict[str, Any] | None
            The added object if `return_obj` is `True`, otherwise `None`.
        """
        ...

    @overload
    def add_all(
        self,
        objs: list[DomainModel],
        return_objs: Literal[True],
        serialize: bool | None,
        use_factory: Literal[True, None],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        one_by_one: bool,
        **params: Any,
    ) -> list[DomainModel]: ...

    @overload
    def add_all(
        self,
        objs: list[DomainModel],
        return_objs: Literal[True],
        serialize: bool | None,
        use_factory: Literal[False],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        one_by_one: bool,
        **params: Any,
    ) -> list[dict[str, Any]]: ...

    @overload
    def add_all(
        self,
        objs: list[DomainModel],
        return_objs: Literal[False],
        serialize: bool | None,
        use_factory: bool | None,
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        one_by_one: bool,
        **params: Any,
    ) -> None: ...

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
        return_objs
            Whether to return the added objects or not.
        serialize
            Whether to serialize the objects before sending them in the API
            request.
        use_factory
            Whether to use the model factory method for creating models from
            response data.
        endpoint
            The API endpoint to which the objects should be added.
        parent_endpoint
            The parent API endpoint, if the resources are nested under a parent
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
        list[DomainModel] | list[dict[str, Any]] | None
            The added objects if `return_obj` is `True`, otherwise `None`.
        """
        ...

    @overload
    def get(
        self,
        use_factory: Literal[True, None],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> DomainModel: ...

    @overload
    def get(
        self,
        use_factory: Literal[False],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> dict[str, Any]: ...

    def get(
        self,
        use_factory: bool | None = None,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        param: str | int | UUID | None = None,
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
        DomainModel | dict[str, Any]
            The retrieved object.
        """
        ...

    @overload
    def get_all(
        self,
        use_factory: Literal[True, None],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> list[DomainModel]: ...

    @overload
    def get_all(
        self,
        use_factory: Literal[False],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> list[dict[str, Any]]: ...

    def get_all(
        self,
        use_factory: bool | None = None,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        param: str | int | UUID | None = None,
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
        list[DomainModel] | list[dict[str, Any]]
            The retrieved objects.
        """
        ...

    @overload
    def patch(
        self,
        patch: JsonPatch,
        return_obj: Literal[True],
        use_factory: Literal[True, None],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> DomainModel: ...

    @overload
    def patch(
        self,
        patch: JsonPatch,
        return_obj: Literal[True],
        use_factory: Literal[False],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> dict[str, Any]: ...

    @overload
    def patch(
        self,
        patch: JsonPatch,
        return_obj: Literal[False],
        use_factory: bool | None,
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> None: ...

    def patch(
        self,
        patch: JsonPatch,
        return_obj: bool = True,
        use_factory: bool | None = None,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        param: str | int | UUID | None = None,
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
        DomainModel | dict[str, Any] | None
            The updated object if `return_obj` is `True`, otherwise `None`.
        """
        ...

    def remove(
        self,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        param: str | int | UUID | None = None,
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
        ...

    @overload
    def update(
        self,
        obj: DomainModel,
        return_obj: Literal[True],
        serialize: bool | None,
        use_factory: Literal[True, None],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> DomainModel: ...

    @overload
    def update(
        self,
        obj: DomainModel,
        return_obj: Literal[True],
        serialize: bool | None,
        use_factory: Literal[False],
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> dict[str, Any]: ...

    @overload
    def update(
        self,
        obj: DomainModel,
        return_obj: Literal[False],
        serialize: bool | None,
        use_factory: bool | None,
        endpoint: str | None,
        parent_endpoint: str | None,
        parent_param: str | int | UUID | None,
        param: str | int | UUID | None,
        model: DomainModel | None,
        additional_request_params: dict[str, Any] | None,
        **params: Any,
    ) -> None: ...

    def update(
        self,
        obj: DomainModel,
        return_obj: bool = True,
        serialize: bool | None = None,
        use_factory: bool | None = None,
        endpoint: str | None = None,
        parent_endpoint: str | None = None,
        parent_param: str | int | UUID | None = None,
        param: str | int | UUID | None = None,
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
        DomainModel | dict[str, Any] | None
            The updated object if `return_obj` is `True`, otherwise `None`.
        """
        ...
