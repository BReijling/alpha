"""RepositoryModel dataclass definition"""

from dataclasses import dataclass

from alpha.domain.models.base_model import BaseDomainModel
from alpha.interfaces.sql_repository import SqlRepository


@dataclass
class RepositoryModel:
    """Model representing a repository configuration"""

    name: str
    repository: type[SqlRepository[BaseDomainModel]]
    default_model: type[BaseDomainModel]
    interface: object | None
