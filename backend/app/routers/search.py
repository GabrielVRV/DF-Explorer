from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.db import get_session
from app.models import Database, Table, TableField, TableIndex, IndexField

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(q: str = Query(..., min_length=2), session: Session = Depends(get_session)):
    like = f"%{q}%"

    table_rows = session.exec(
        select(Table, Database)
        .join(Database, Table.database_id == Database.id)
        .where(Table.name.ilike(like))
    ).all()

    field_rows = session.exec(
        select(TableField, Table, Database)
        .join(Table, TableField.table_id == Table.id)
        .join(Database, Table.database_id == Database.id)
        .where(TableField.name.ilike(like))
    ).all()

    index_rows = session.exec(
        select(TableIndex, Table, Database)
        .join(Table, TableIndex.table_id == Table.id)
        .join(Database, Table.database_id == Database.id)
        .where(TableIndex.name.ilike(like))
    ).all()

    tables = [
        {
            "database": database.name,
            "table": table.name,
            "dump_name": table.dump_name,
            "area": table.area,
        }
        for table, database in table_rows
    ]

    fields = [
        {
            "database": database.name,
            "table": table.name,
            "field": table_field.name,
            "data_type": table_field.data_type,
            "format": table_field.format,
            "max_width": table_field.max_width,
            "mandatory": table_field.mandatory,
            "label": table_field.label,
        }
        for table_field, table, database in field_rows
    ]

    indexes = []
    for index, table, database in index_rows:
        index_fields = session.exec(
            select(IndexField).where(IndexField.index_id == index.id).order_by(IndexField.position)
        ).all()
        indexes.append(
            {
                "database": database.name,
                "table": table.name,
                "index": index.name,
                "is_unique": index.is_unique,
                "is_primary": index.is_primary,
                "fields": [
                    {"name": f.field_name, "ascending": f.ascending} for f in index_fields
                ],
            }
        )

    return {"tables": tables, "fields": fields, "indexes": indexes}


@router.get("/tables/{database_name}/{table_name}")
def table_detail(database_name: str, table_name: str, session: Session = Depends(get_session)):
    database = session.exec(select(Database).where(Database.name == database_name)).first()
    if not database:
        return {"error": "database not found"}

    table = session.exec(
        select(Table).where(Table.database_id == database.id, Table.name == table_name)
    ).first()
    if not table:
        return {"error": "table not found"}

    fields = session.exec(
        select(TableField).where(TableField.table_id == table.id).order_by(TableField.position)
    ).all()

    indexes = session.exec(select(TableIndex).where(TableIndex.table_id == table.id)).all()
    index_details = []
    for index in indexes:
        index_fields = session.exec(
            select(IndexField).where(IndexField.index_id == index.id).order_by(IndexField.position)
        ).all()
        index_details.append(
            {
                "name": index.name,
                "is_unique": index.is_unique,
                "is_primary": index.is_primary,
                "fields": [{"name": f.field_name, "ascending": f.ascending} for f in index_fields],
            }
        )

    return {
        "database": database.name,
        "table": table.name,
        "area": table.area,
        "fields": [
            {
                "name": f.name,
                "data_type": f.data_type,
                "format": f.format,
                "max_width": f.max_width,
                "mandatory": f.mandatory,
                "label": f.label or f.column_label,
                "description": f.description or f.help_text,
            }
            for f in fields
        ],
        "indexes": index_details,
    }
