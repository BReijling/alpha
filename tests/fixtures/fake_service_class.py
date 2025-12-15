import sys
from typing import Any, Optional


class FakeService:
    def simple_types(
        self, string: str, integer: int, floating_point: float, boolean: bool
    ) -> dict[str, Any]:
        return {
            'string': string,
            'integer': integer,
            'floating_point': floating_point,
            'boolean': boolean,
        }

    def typing_union_generic_alias(
        self,
        optional_boolean: Optional[bool],
        optional_any_list: Optional[list[Any]],
        optional_str_list: Optional[list[str]],
        optional_int_list: Optional[list[int]],
    ) -> dict[str, Any]:
        return {
            'optional_boolean': optional_boolean,
            'optional_any_list': optional_any_list,
            'optional_str_list': optional_str_list,
            'optional_int_list': optional_int_list,
        }

    if sys.version_info.minor >= 10:

        def types_union_type(
            self,
            optional_boolean: bool | None,
            optional_any_list: list[Any] | None,
            optional_str_list: list[str] | None,
            optional_int_list: list[int] | None,
        ) -> dict[str, Any]:
            return {
                'optional_boolean': optional_boolean,
                'optional_any_list': optional_any_list,
                'optional_str_list': optional_str_list,
                'optional_int_list': optional_int_list,
            }
