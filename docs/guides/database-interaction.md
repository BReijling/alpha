# Database interaction

In this guide, we will cover how to interact with databases using Alpha's database and repository patterns. We will discuss how to set up a database connection, perform basic CRUD operations, and manage database sessions effectively. This guide assumes you have a basic understanding of databases and SQL. As mentioned in the [Design Principles](../concepts/design-principles.md) guide, database interactions in Alpha are designed to align with the principles of Domain-Driven Design (DDD), ensuring a clear separation of concerns and maintainable code. We will also touch on how to implement the repository pattern to abstract away database access and provide a clean interface for your application logic. We end by discussing the [`SqlAlchemyUnitOfWork`][alpha.adapters.sqla_unit_of_work.SqlAlchemyUnitOfWork] implementation, which provides a convenient way to manage database transactions and sessions in a consistent manner across your application. By the end of this guide, you should have a solid understanding of how to work with databases in an Alpha application and how to structure your code for maintainability and scalability.

## SqlAlchemy Database Connector

Alpha provides a [`SqlAlchemyDatabase`][alpha.infra.connectors.sql_alchemy.SqlAlchemyDatabase] connector, which is an implementation of the [`SqlDatabase`][alpha.interfaces.sql_database.SqlDatabase] interface, that allows you to connect to various SQL databases supported by SQLAlchemy. This connector abstracts away the complexities of database connections and provides a simple interface for executing queries and managing transactions. You can configure the [`SqlAlchemyDatabase`][alpha.infra.connectors.sql_alchemy.SqlAlchemyDatabase] connector with your database connection string and use it to perform CRUD operations in your application. The connector also supports connection pooling and session management, making it suitable for production applications. To use the [`SqlAlchemyDatabase`][alpha.infra.connectors.sql_alchemy.SqlAlchemyDatabase] connector, you will need to install SQLAlchemy and the appropriate database driver for your database (e.g., `psycopg2` for PostgreSQL, `mysqlclient` for MySQL). The `postgresql` and/or `mysql` library extras can be installed to include the necessary drivers. Once you have the connector set up, you can create repositories that use it to interact with the database, allowing you to keep your database access code organized and maintainable.

### Example Usage

Here is a simple example of how to set up the [`SqlAlchemyDatabase`][alpha.infra.connectors.sql_alchemy.SqlAlchemyDatabase] connector and use it in a repository:

```python
from sqlalchemy import text

from alpha import SqlAlchemyDatabase

# Configure the database connector
database = SqlAlchemyDatabase(
    host="localhost",
    port=5432,
    username="user",
    password="password",
    db_name="mydatabase",
    db_type="postgresql",
    schema_name="public",
)

# Alternatively, use a connection string from configuration
database = SqlAlchemyDatabase(conn_str="postgresql://user:password@localhost:5432/mydatabase")

# Get a session and execute a query
with database.get_session() as session:
    result = session.execute(text("SELECT * FROM users"))
    for row in result:
        print(row)
```   

## SqlRepository Pattern

The repository pattern is a design pattern that provides a way to abstract away the details of data access and manipulation. In Alpha, you can implement repositories that use the [`SqlAlchemyDatabase`][alpha.infra.connectors.sql_alchemy.SqlAlchemyDatabase] connector to interact with your database. A repository typically provides methods for performing CRUD operations on a specific entity or aggregate root, allowing you to keep your database access code organized and maintainable. By using repositories, you can also easily swap out the underlying database implementation if needed, without affecting the rest of your application logic.

The [`SqlAlchemyRepository`][alpha.repositories.sql_alchemy_repository.SqlAlchemyRepository] class is an implementation of the [`SqlRepository`][alpha.interfaces.sql_repository.SqlRepository] interface. It provides common methods for adding, updating, deleting, and querying entities in the database. You can also inherit from [`SqlAlchemyRepository`][alpha.repositories.sql_alchemy_repository.SqlAlchemyRepository] to create specific repositories for your entities, where you can add custom query methods as needed. The repository pattern helps to keep your application logic clean and focused on the domain, while the repository handles all interactions with the database.

### Object-Relational Mapping (ORM)

While the [`SqlAlchemyDatabase`][alpha.infra.connectors.sql_alchemy.SqlAlchemyDatabase] connector allows you to execute raw SQL queries, it is often more convenient to use an Object-Relational Mapping (ORM) approach. SQLAlchemy provides a powerful ORM that allows you to define your database models as Python classes and interact with them using Python code instead of raw SQL. This can make your code more readable and maintainable, as well as provide additional features like automatic schema generation and relationship management. To use SQLAlchemy's ORM with the [`SqlAlchemyDatabase`][alpha.infra.connectors.sql_alchemy.SqlAlchemyDatabase] connector, you can define your models using SQLAlchemy's declarative base and then use the [`SqlAlchemyRepository`][alpha.repositories.sql_alchemy_repository.SqlAlchemyRepository] to perform operations on those models. This approach allows you to take full advantage of SQLAlchemy's capabilities while still benefiting from the abstraction provided by the repository pattern. 

Alternatively you can map your domain models to SQLAlchemy models in an imperative way using a mapping layer, allowing you to keep your domain models clean and free of any database-specific code. This can be implemented using a separate class for mapping. The class should be an implementation of the [`SqlMapper`][alpha.interfaces.sql_mapper.SqlMapper] interface. The [`SqlAlchemyDatabase`][alpha.infra.connectors.sql_alchemy.SqlAlchemyDatabase] connector is able to handle this approach as well by setting the `mapper` parameter to your mapping class, which will be responsible for converting between your domain models and the SQLAlchemy models used for database interactions. The second example below demonstrates how to implement a mapping layer for your domain models.

### Example Repository

Here is an example of how to use the [`SqlAlchemyRepository`][alpha.repositories.sql_alchemy_repository.SqlAlchemyRepository]:

```python
from alpha import SqlAlchemyRepository, SqlAlchemyDatabase
from my_app.models import User

db = SqlAlchemyDatabase(...)

with db.get_session() as session:
    users = SqlAlchemyRepository[User](session=session, default_model=User)

    # Get a user by ID
    user = users.get_by_id(1)
```

Here is an example of how to create a custom repository for a [`User`][alpha.domain.models.user.User] entity by inheriting the [`SqlAlchemyRepository`][alpha.repositories.sql_alchemy_repository.SqlAlchemyRepository]. A [`SqlMapper`][alpha.interfaces.sql_mapper.SqlMapper] is also being used to perform imperative mapping between the User model and "users" table:

```python
import sqlalchemy as sa
from sqlalchemy.orm import registry

from alpha import SqlAlchemyRepository, SqlAlchemyDatabase
from my_app.models import User

class OrmMapper:
    convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    mapper_registry = registry()
    metadata = sa.MetaData(naming_convention=convention)
    started = False

    users = sa.Table(
        "users",
        metadata,
        sa.Column(
            "id",
            sa.String,
            primary_key=True,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("username", sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column("email", sa.VARCHAR(255), nullable=True),
        sa.Column("display_name", sa.VARCHAR(255), nullable=True),
        sa.Column("role", sa.VARCHAR(50), nullable=True),
        sa.Column("is_active", sa.BOOLEAN, nullable=False, default=True),
        sa.Column("admin", sa.BOOLEAN, nullable=False, default=False),
    )

    @classmethod
    def start_mapping(cls):
        cls.mapper_registry.map_imperatively(User, cls.users)
        cls.started = True

class UserRepository(SqlAlchemyRepository[User]):
    def find_by_email(self, email: str) -> User | None:
        return self.query().filter(User.email == email).first()

# Usage
db = SqlAlchemyDatabase(..., mapper=OrmMapper)
with db.get_session() as session:
    users_repo = UserRepository(session=session, default_model=User)

    user = users_repo.find_by_email("alpha@alpha.abc")
```

## Unit-of-Work Pattern

The Unit-of-Work pattern is a design pattern that helps manage database transactions and sessions in a consistent manner. In Alpha, you can implement a [`SqlAlchemyUnitOfWork`][alpha.adapters.sqla_unit_of_work.SqlAlchemyUnitOfWork] that uses the [`SqlAlchemyDatabase`][alpha.infra.connectors.sql_alchemy.SqlAlchemyDatabase] connector to manage database sessions and transactions. The unit of work provides a context for performing multiple operations on the database as a single transaction, ensuring that either all operations succeed or none of them are applied. This is particularly useful for maintaining data integrity and consistency in your application. By using the unit-of-work pattern, you can also simplify error handling and rollback logic, as the unit of work will automatically handle these concerns for you.

### Example Unit-of-Work

Here is an example of how to use the [`SqlAlchemyUnitOfWork`][alpha.adapters.sqla_unit_of_work.SqlAlchemyUnitOfWork]:

```python
from alpha import (
    SqlAlchemyUnitOfWork,
    SqlAlchemyRepository,
    SqlAlchemyDatabase,
    RepositoryModel
)
from my_app.models import User

db = SqlAlchemyDatabase(...)

repositories = [
    RepositoryModel(
        name="users",
        repository=SqlAlchemyRepository[User],
        default_model=User,
    )
]

uow = SqlAlchemyUnitOfWork(db=db, repos=repositories)

# Example of using the unit of work to get a user
with uow:
    user = uow.users.get_by_id(1)

# Example of using the unit of work to add a new user
new_user = User(name="Alpha User", email="random@alpha.abc")
with uow:
    uow.users.add(new_user)
    uow.commit()
```

## Example for production use

In a production application, you would typically set up your database connection and unit of work in a dependency injection container, allowing you to easily manage and inject these dependencies throughout your application. Here is an example of how to configure the [`SqlAlchemyDatabase`][alpha.infra.connectors.sql_alchemy.SqlAlchemyDatabase] connector and [`SqlAlchemyUnitOfWork`][alpha.adapters.sqla_unit_of_work.SqlAlchemyUnitOfWork] in a dependency injection container:

```python
from dependency_injector import containers, providers

from alpha import (
    SqlAlchemyDatabase,
    SqlAlchemyUnitOfWork,
    RepositoryModel,
    UserLifecycleManagement,
    User,
    Group,
)
from my_app.mappers import Mapper

class Container(containers.DeclarativeContainer):
    """Dependency injection container for the tests."""

    config = providers.Configuration()

    database = providers.Singleton(
        SqlAlchemyDatabase,
        host=config.database.host,
        port=config.database.port,
        username=config.database.username,
        password=config.database.password,
        db_name=config.database.db_name,
        db_type=config.database.db_type,
        create_schema=False,
        create_tables=True,
        mapper=Mapper,
    )

    repositories = providers.List(
        RepositoryModel(
            name="users",
            repository=SqlAlchemyRepository[User],
            default_model=User,
            interface=SqlRepository,
        ),
        RepositoryModel(
            name="groups",
            repository=SqlAlchemyRepository[Group],
            default_model=Group,
            interface=SqlRepository,
        ),
    )

    unit_of_work = providers.Factory(
        SqlAlchemyUnitOfWork,
        db=database,
        repos=repositories,
    )

    user_management_service: providers.Factory[UserLifecycleManagement] = (
        providers.Factory(
            UserLifecycleManagement,
            uow=unit_of_work,
        )
    )
```
