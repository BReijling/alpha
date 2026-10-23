# API Reference - Domain models

Reference documentation for all domain model classes.

All documentation is auto-generated from docstrings in the source code.

## Models

| Models | Description |
|---|---|
| [BaseDomainModel](models/base_model.md) | Base class for all domain models which can be inherited by all domain models in the application |
| [LifeCycleBase](models/life_cycle_base.md) | Base class for lifecycle model attributes which can be inherited by all domain models in the application |
| [User](models/user.md) | Domain model which represents a user in the system |
| [UserWithGroupObjects](models/user.md) | Domain model which represents a user along with their associated group objects |
| [UserWithObjects](models/user.md) | Domain model which represents a user along with their associated group and permissionobjects |
| [Group](models/group.md) | Domain model which represents a group of users with specific permissions |
| [GroupWithObjects](models/group.md) | Domain model which represents a group along with its associated permission objects |
| [Permission](models/permission.md) | Domain model which represents a system permission |
| [Role](models/role.md) | Enum class which defines user roles with varying levels of permissions |
