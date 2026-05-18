from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.config import DATA_DIR, settings

DATA_DIR.mkdir(parents=True, exist_ok=True)

_db_url = make_url(settings.db_url)
if _db_url.drivername == "sqlite" and _db_url.database and _db_url.database != ":memory:":
    _p = Path(_db_url.database)
    if not _p.is_absolute():
        _p = Path.cwd() / _p
    _p.parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.db_url.startswith("sqlite") else {}
engine = create_engine(settings.db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
