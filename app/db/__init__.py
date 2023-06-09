import contextlib
from reprlib import recursive_repr
from typing import TypeVar

import sqlalchemy.orm
from sqlalchemy.orm import DeclarativeBase

import alembic.config
import alembic.migration
import alembic.script
from app.common.config import config


class Base(DeclarativeBase):
    pass


engine = sqlalchemy.create_engine(config.DATABASE_URL, **config.DATABASE_CONFIG)
SessionLocal = sqlalchemy.orm.sessionmaker(bind=engine)

OrmModel = TypeVar("OrmModel", bound=Base)


def get_db_session():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


new_db_session = contextlib.contextmanager(get_db_session)


def check_database_is_up_to_date() -> bool:
    alembic_config_file = "alembic.ini"
    alembic_config = alembic.config.Config(alembic_config_file)
    directory = alembic.script.ScriptDirectory.from_config(alembic_config)
    with engine.begin() as connection:
        context = alembic.migration.MigrationContext.configure(connection)
        return set(context.get_current_heads()) == set(directory.get_heads())


def table_repr(cls: type[OrmModel]) -> type[OrmModel]:
    def field_repr(obj: OrmModel) -> str:
        field_strs = [
            f"{field_name}={getattr(obj, field_name)}"
            for field_name in obj.__table__.columns.keys()
        ]
        class_name = obj.__class__.__name__
        return f"<{class_name}: {','.join(field_strs)}>"

    cls.__repr__ = recursive_repr()(field_repr)
    return cls
