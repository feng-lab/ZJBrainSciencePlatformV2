import sqlalchemy.ext.declarative
import sqlalchemy.orm

import alembic.config
import alembic.migration
import alembic.script
from app.common.config import config

engine = sqlalchemy.create_engine(config.DATABASE_URL, **config.DATABASE_CONFIG)
SessionLocal = sqlalchemy.orm.sessionmaker(bind=engine)
Base = sqlalchemy.ext.declarative.declarative_base()


def get_db_session():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


def check_database_is_up_to_date() -> bool:
    alembic_config_file = "alembic.ini"
    alembic_config = alembic.config.Config(alembic_config_file)
    directory = alembic.script.ScriptDirectory.from_config(alembic_config)
    with engine.begin() as connection:
        context = alembic.migration.MigrationContext.configure(connection)
        return set(context.get_current_heads()) == set(directory.get_heads())
