from typing import ClassVar

from sqlalchemy.orm import registry
import sqlalchemy as sa

from .models import TestGroup
from .models import TestUser
from .models import TestToken


class TestMapper:
    started: ClassVar[bool] = False

    schema_name: ClassVar[str] = "public"

    mapper_registry: ClassVar = registry()

    convention: ClassVar = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    metadata: ClassVar = sa.MetaData(naming_convention=convention)

    users = sa.Table(
        "test_users",
        metadata,
        sa.Column(
            "id",
            sa.String,
            primary_key=True,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("username", sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column("password", sa.VARCHAR(200), nullable=True),
        sa.Column("email", sa.VARCHAR(255), nullable=True),
        sa.Column("display_name", sa.VARCHAR(255), nullable=True),
        sa.Column("role", sa.VARCHAR(50), nullable=True),
        sa.Column("permissions", sa.ARRAY(sa.VARCHAR(50)), nullable=True),
        sa.Column("groups", sa.ARRAY(sa.VARCHAR(50)), nullable=True),
        sa.Column("is_active", sa.BOOLEAN, nullable=False, default=True),
        sa.Column("admin", sa.BOOLEAN, nullable=False, default=False),
    )

    groups = sa.Table(
        "test_groups",
        metadata,
        sa.Column(
            "id",
            sa.String,
            primary_key=True,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column("description", sa.VARCHAR(255), nullable=True),
        sa.Column("permissions", sa.ARRAY(sa.VARCHAR(50)), nullable=True),
        sa.Column("is_active", sa.BOOLEAN, nullable=False, default=True),
    )

    refresh_tokens = sa.Table(
        "test_refresh_tokens",
        metadata,
        sa.Column(
            "id",
            sa.String,
            primary_key=True,
            unique=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "value", sa.VARCHAR(255), nullable=False, unique=True, index=True
        ),
        sa.Column("token_type", sa.VARCHAR(10), nullable=False),
        sa.Column("subject", sa.VARCHAR(50), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    @classmethod
    def start_mapping(cls):
        cls.mapper_registry.map_imperatively(TestUser, cls.users)
        cls.mapper_registry.map_imperatively(TestGroup, cls.groups)
        cls.mapper_registry.map_imperatively(TestToken, cls.refresh_tokens)

        cls.started = True
