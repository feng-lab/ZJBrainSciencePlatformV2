import sqlalchemy.ext.declarative
import sqlalchemy.orm

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
