import sqlalchemy.ext.declarative
import sqlalchemy.orm

from app.utils import is_debug_mode

if is_debug_mode():
    # 开发环境，使用SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///../test-db.sqlite3"
    SQLALCHEMY_DATABASE_ARGS = {
        "echo": True,
        "future": True,
        "connect_args": {
            "check_same_thread": False,
        },
    }
else:
    # TODO 正式环境，要配置好MySQL
    SQLALCHEMY_DATABASE_URL = ""
    SQLALCHEMY_DATABASE_ARGS = {}

# 数据库引擎
engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL, **SQLALCHEMY_DATABASE_ARGS)

# 数据库会话类
SessionLocal = sqlalchemy.orm.sessionmaker(
    bind=engine, autoflush=False, autocommit=False
)

# ORM模型基类
Base = sqlalchemy.ext.declarative.declarative_base()
