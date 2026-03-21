"""RepositoryModel dataclass definition"""

from dataclasses import dataclass

from alpha.domain.models.base_model import BaseDomainModel
from alpha.interfaces.repository import Repository


@dataclass
class RepositoryModel:
    """Model representing a repository configuration"""

    name: str
    repository: type[Repository[BaseDomainModel]]
    default_model: BaseDomainModel
    interface: object | None
    additional_config: dict[str, object] | None = None
