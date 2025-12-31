"""Contains ResponseFactory class"""

import json
from dataclasses import MISSING, is_dataclass
from enum import Enum
from typing import Any, Iterable, get_args, get_origin

from alpha import exceptions
from alpha.encoder import JSONEncoder
from alpha.interfaces.dataclass_instance import DataclassInstance
from alpha.interfaces.openapi_model import OpenAPIModel
from alpha.utils.is_attrs import is_attrs


class ResponseFactory:
    """Mapping a dataclass instance to an OpenAPI model class"""

    def process(
        self,
        response: DataclassInstance | Iterable[DataclassInstance],
        cls: OpenAPIModel | Iterable[OpenAPIModel],
    ) -> object:
        """Mapping a dataclass instance or a collection of instances to an
        OpenAPI model

        Parameters
        ----------
        response
            DomainModel instance
        cls
            OpenAPI model class or an Iterable

        Returns
        -------
            OpenAPI model instance or a list of instances

        Raises
        ------
        exceptions.ClassMismatchException
            The targeted object type is a list but the source object is not
            iterable
        Exception
            Encountered unexpected exception
        ValueError
            Unable to instantiate a class of type OpenAPIModel without values.
            Probably because there are required values which cannot be None
        TypeError
            cls value is not a valid OpenAPIModel type
        """

        cls_origin = get_origin(cls)

        # When the source instance and target class are of an iterable type
        if cls_origin in [list, tuple, set]:
            if isinstance(response, Iterable):
                arg = get_args(cls)[0]
                return [
                    self.process(response=obj, cls=arg) for obj in response
                ]
            if cls_origin != get_origin(response):
                raise exceptions.ClassMismatchException(
                    "The targeted object type is a list but the source object "
                    "is not iterable"
                )
            raise Exception(
                f"Encountered unexpected exception; cls_origin: {cls_origin}, "
                + f"response: {response}"
            )

        attrs: dict[str, type]
        # Check if the openapi_types variable is set as a class variable
        if len(cls.openapi_types) > 0:  # type: ignore
            attrs = getattr(cls, "openapi_types")
        # Else try to instantiate the class and read the openapi_types value
        else:
            try:
                cls_instance: Any = cls()  # type: ignore
            except ValueError as e:
                raise ValueError(
                    "Unable to instantiate a class of type OpenAPIModel "
                    "without values. Probably because there are required "
                    f"values which cannot be None: '{e}'. A solution to "
                    "this problem is to set the 'openapi_types' attribute "
                    "as a class variable instead of setting it in the "
                    "__init__ method"
                )
            error_msg = (
                f"'{cls.__name__}' is not a "  # type: ignore
                "valid OpenAPIModel type"
            )
            if not hasattr(cls_instance, "openapi_types"):
                raise TypeError(error_msg)
            attrs = getattr(cls_instance, "openapi_types")

        # Process attrs through _attr_factory
        params = {
            attr_name: self._attr_factory(
                attr_name=attr_name, attr_type=attr_type, response=response
            )
            for attr_name, attr_type in attrs.items()
        }

        return cls(**params)  # type: ignore

    def _attr_factory(
        self, attr_name: str, attr_type: type, response: object
    ) -> Any:
        """Handles the attributes of an object by returning the response value
        in the correct form

        Parameters
        ----------
        attr_name
            The name of the attribute
        attr_type
            The type of the attribute. This can be
        response
            A dataclass instance or an list of instances

        Returns
        -------
        Any
            The value from the response object which corresponds to the
            attr_name
        """
        response_value = self._attr_lookup(obj=response, attr_name=attr_name)

        if isinstance(response_value, Enum):
            return response_value.name

        # These if statements are needed to achieve a certain behavior
        if isinstance(attr_type, OpenAPIModel) or (
            get_origin(attr_type) is list
        ):
            if get_origin(attr_type) is list:
                first_item = get_args(attr_type)[0]
                if not isinstance(first_item, OpenAPIModel):
                    return response_value
            return self.process(response=response_value, cls=attr_type)  # type: ignore
        return response_value

    def _attr_lookup(self, obj: object, attr_name: str) -> Any:
        """Lookup the attributes value from an object. The object can be of a
        random type, including a dataclass or a dictionary.

        Parameters
        ----------
        obj
            The source object
        attr_name
            Attribute name

        Returns
        -------
            Any value which corresponds to the attributes name

        Raises
        ------
        exceptions.MissingAttributeError
            Raises in case the attribute is not found
        """
        if hasattr(obj, attr_name):
            return getattr(obj, attr_name, None)

        if is_dataclass(obj) or is_attrs(obj):
            attrs = getattr(obj, "__match_args__", [])

            for attr in attrs:
                obj_attr = getattr(obj, attr, MISSING)

                if attr == attr_name:
                    return obj_attr

                # Lookup nested attribute
                if hasattr(obj_attr, attr_name):
                    return getattr(obj_attr, attr_name)

        if isinstance(obj, dict):
            if attr_name in obj.keys():
                value: Any = obj[attr_name]
                return value

        raise exceptions.MissingAttributeError(
            f"'{attr_name}' can not be found in the response object:"
            + f"{json.dumps(obj, cls=JSONEncoder)}"
        )
