from typing import Optional
from sqlmodel import SQLModel, Field


class Database(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    source_file: str


class Table(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    database_id: int = Field(foreign_key="database.id", index=True)
    name: str = Field(index=True)
    dump_name: Optional[str] = None
    area: Optional[str] = None
    description: Optional[str] = None


class TableField(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    table_id: int = Field(foreign_key="table.id", index=True)
    name: str = Field(index=True)
    data_type: Optional[str] = None
    format: Optional[str] = None
    initial: Optional[str] = None
    label: Optional[str] = None
    column_label: Optional[str] = None
    help_text: Optional[str] = None
    position: Optional[int] = None
    max_width: Optional[int] = None
    mandatory: bool = False
    description: Optional[str] = None


class TableIndex(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    table_id: int = Field(foreign_key="table.id", index=True)
    name: str = Field(index=True)
    area: Optional[str] = None
    is_unique: bool = False
    is_primary: bool = False


class IndexField(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    index_id: int = Field(foreign_key="tableindex.id", index=True)
    field_name: str
    ascending: bool = True
    position: int = 0
