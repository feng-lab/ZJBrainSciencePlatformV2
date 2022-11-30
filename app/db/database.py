import databases
import sqlalchemy
from ormar import ModelMeta

from app.config import config

metadata = sqlalchemy.MetaData()
database = databases.Database(config.DATABASE_URL, **config.DATABASE_CONFIG)
engine = sqlalchemy.create_engine(config.DATABASE_URL, **config.DATABASE_CONFIG)


class BaseMeta(ModelMeta):
    database = database
    metadata = metadata
