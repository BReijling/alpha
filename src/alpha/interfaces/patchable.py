from typing import Protocol

from alpha.domain.models.base_model import DomainModelCovariant
from alpha.infra.models.json_patch import JsonPatch


class Patchable(Protocol[DomainModelCovariant]):
    def patch(self, patches: JsonPatch) -> DomainModelCovariant: ...
