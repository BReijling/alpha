from dataclasses import Field, dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Set, Tuple, Union
from alpha.infra.models.json_patch import JsonPatch
from alpha.interfaces.factories import FactoryClassesInstance
from alpha.interfaces.openapi_model import OpenAPIModel
from tests.fixtures._domain_models import CarType


class FakeDefaultFactory:
    def process(self, field: Field[Any]):
        return field.name


class FakeClassFactory:
    def __init__(self, name: str) -> None:
        self.name = name

    def process(
        self,
        obj: OpenAPIModel,
        field: Field[Any],
        factory_classes: FactoryClassesInstance,
    ) -> Any:
        return self.name


class FakeTypeFactory:
    def __init__(self, name: str = "FakeTypeFactory") -> None:
        self.name = name

    def process(self, key: str, value: Any, cls: Any, **kwargs: dict[str, Any]) -> Any:
        return self.name


class FakeModelClassFactory:
    def __init__(self, name: str) -> None:
        self.name = name

    def process(
        self,
        obj: OpenAPIModel,
        cls: Any,
    ) -> Any:
        return self.name


@dataclass
class FakeDefaultFactoryClass:
    no_default: str
    none_default: str | None
    string_default: str = "string"
    date_time: datetime = field(default=datetime.now)  # type: ignore
    list_factory: list[str] = field(default_factory=list)


class FakeToDictClass:
    def to_dict(self):
        return "to_dict"


class FakeAsDictClass:
    def _asdict(self):
        return "_asdict"


class FakeDunderDictClass:
    @property
    def __dict__(self):  # type: ignore
        return "__dict__"


@dataclass
class FakeDictFactoryClass:
    obj: dict[str, str]
    string_param: str = "string"
    to_dict_param: FakeToDictClass = FakeToDictClass()
    asdict_param: FakeAsDictClass = FakeAsDictClass()
    dict_param: FakeDunderDictClass = FakeDunderDictClass()


@dataclass
class FakeDataclass:
    field: str = "field"


@dataclass
class FakeAllTypeClass:
    types_list: list[str]
    typing_list: List[str]
    types_tuple: tuple[str]
    typing_tuple: Tuple[str]
    types_set: set[str]
    typing_set: Set[str]
    types_dict: dict[str, str]
    typing_dict: Dict[str, str]
    types_list_union: list[str | int]
    typing_list_union: List[Union[str, int]]
    enum_list: list[CarType]
    types_union: int | float
    types_union2: int | float
    typing_union: Union[int, float]
    optional_list: list[str] | None
    optional_dataclass: FakeDataclass | None
    no_str: str
    str_: str
    int_: int
    float_: float
    complex_: complex
    bool_: bool
    date_: date
    datetime_: datetime
    dataclass_: FakeDataclass
    list_dataclass: list[FakeDataclass]
    no_list_dataclass: list[FakeDataclass]
    json_patch: JsonPatch
