"""RepositoryModel dataclass definition"""

from dataclasses import dataclass
from typing import Callable, Generic

from alpha.domain.models.base_model import DomainModel


@dataclass
class RepositoryModel(Generic[DomainModel]):
    """Model representing a repository configuration

    Attributes
    ----------
    name
        The name of the repository
    repository
        A Repository class or factory function that can be called to create an
        instance of the repository
    default_model
        The default domain model class that the repository will manage
    interface
        An optional interface that the repository implements, used for type
        checking and dependency injection
    additional_config
        An optional dictionary for any additional configuration parameters
        needed to instantiate the repository
    """

    name: str
    repository: Callable[..., object]
    default_model: type[DomainModel]
    interface: object | None = None
    additional_config: dict[str, object] | None = None
