import os
from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine

DATA_DIR = Path(os.environ.get("DF_EXPLORER_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "schema.db"
engine = create_engine(f"sqlite:///{DB_PATH}")


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
