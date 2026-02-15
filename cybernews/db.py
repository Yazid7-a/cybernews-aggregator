from __future__ import annotations

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from cybernews.models import Base

def init_db(db_url: str):
    engine = create_engine(db_url, future=True)
    Base.metadata.create_all(engine)
    return engine

@contextmanager
def get_session(engine):
    session = Session(engine, future=True)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
