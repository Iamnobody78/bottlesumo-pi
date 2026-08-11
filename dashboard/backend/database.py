"""数据库引擎与会话管理 (SQLite)。"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base  # noqa: E402

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db")
DB_PATH = os.getenv("GOV_DASH_DB", os.path.join(DB_DIR, "governance.db"))


def build_engine(db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})


def build_session_factory(engine=None):
    engine = engine or build_engine()
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_session_factory():
    """模块级默认工厂 (FastAPI 依赖注入用)。"""
    global _factory
    if _factory is None:
        _factory = build_session_factory()
    return _factory


_factory = None
