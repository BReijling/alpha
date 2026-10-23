from datetime import UTC, datetime
from typing import Self, Sequence

from alpha.domain.models.base_model import BaseDomainModel


class UpdatableMixin:
    """This mixin class can be used to add an update method to domain models.

    The subclass must define the `__update_fields__` attribute or property,
    which should be a list of field names that are allowed to be updated.

    Example
    -------
    class MyModel(BaseDomainModel, UpdatableMixin):
        __update_fields__ = ["name", "description"]
    """

    @property
    def __update_fields__(self) -> Sequence[str]:
        raise NotImplementedError(
            "Subclasses must implement the __update_fields__ property."
        )

    def update(self, obj: BaseDomainModel) -> Self:
        """Update the current instance with the values from another instance of
        itself. In order to use this method, the subclass must define the
        `__update_fields__` attribute or property, which should be a list of
        field names that are allowed to be updated.

        Additionally, if the model has a `modified_at` or `updated_at`
        attribute, it will be automatically updated to the current UTC time.

        Parameters
        ----------
        obj
            The instance to update from.

        Returns
        -------
        Self
            The updated instance.

        Raises
        ------
        TypeError
            If the provided object is not an instance of the same class.
        """
        if not isinstance(obj, self.__class__):
            raise TypeError(
                "Instance can only be updated from another instance of itself"
            )

        for _field in getattr(self, "__update_fields__"):
            setattr(self, _field, getattr(obj, _field))

        if hasattr(self, "modified_at"):
            setattr(self, "modified_at", datetime.now(tz=UTC))
        if hasattr(self, "updated_at"):
            setattr(self, "updated_at", datetime.now(tz=UTC))
        return self
