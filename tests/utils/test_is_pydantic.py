from alpha.utils.is_pydantic import is_pydantic


class PydanticLikeClass:
    __pydantic_fields__: dict[str, object] = {}


class _RaisingMeta(type):
    call_count = 0

    def __getattr__(cls, name):
        _RaisingMeta.call_count += 1
        raise RuntimeError("should not be called")


class NonPydanticWithRaisingGetattr(metaclass=_RaisingMeta):
    pass


def test_is_pydantic_returns_true_for_class_and_instance() -> None:
    assert is_pydantic(PydanticLikeClass)
    assert is_pydantic(PydanticLikeClass())


def test_is_pydantic_does_not_trigger_dynamic_getattr() -> None:
    _RaisingMeta.call_count = 0

    assert not is_pydantic(NonPydanticWithRaisingGetattr)
    assert _RaisingMeta.call_count == 0
