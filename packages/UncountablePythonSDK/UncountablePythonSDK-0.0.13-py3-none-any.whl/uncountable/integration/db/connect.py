import os
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine


def create_db_engine() -> Engine:
    return create_engine(os.environ["UNC_SQLITE_URI"])

