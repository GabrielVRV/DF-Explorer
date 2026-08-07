import os
import sys
from pathlib import Path
from sqlalchemy import event
from sqlmodel import SQLModel, Session, create_engine


def _default_data_dir() -> Path:
    if getattr(sys, "frozen", False):
        # Empacotado (PyInstaller): guarda os dados fora da pasta temporaria de extracao.
        appdata = os.environ.get("APPDATA", str(Path.home()))
        return Path(appdata) / "DF Explorer" / "data"
    return Path(__file__).resolve().parent.parent / "data"


DATA_DIR = Path(os.environ.get("DF_EXPLORER_DATA_DIR", _default_data_dir()))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "schema.db"
engine = create_engine(f"sqlite:///{DB_PATH}")


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, _record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
