import databases
import sqlalchemy
from ormar import ModelMeta

from config import get_config

metadata = sqlalchemy.MetaData()
database = databases.Database(get_config().DATABASE_URL, **get_config().DATABASE_CONFIG)
engine = sqlalchemy.create_engine(
    get_config().DATABASE_URL, **get_config().DATABASE_CONFIG
)


class BaseMeta(ModelMeta):
    database = database
    metadata = metadata
