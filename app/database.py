import sqlalchemy.ext.declarative
import sqlalchemy.orm

from app.config import config

# 数据库引擎
engine = sqlalchemy.create_engine(config.DATABASE_URL, **config.DATABASE_CONFIG)

# 数据库会话类
SessionLocal = sqlalchemy.orm.sessionmaker(
    bind=engine, autoflush=False, autocommit=False
)

# ORM模型基类
Base = sqlalchemy.ext.declarative.declarative_base()
