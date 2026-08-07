from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from openpyxl import Workbook
from openpyxl.styles import Font
from sqlmodel import Session, select

from app.db import get_session
from app.models import Database, Table, TableField, TableIndex, IndexField

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(q: str = Query(..., min_length=2), session: Session = Depends(get_session)):
    like = f"%{q}%"
    q_lower = q.lower()

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

    tables.sort(key=lambda t: t["table"].lower() != q_lower)
    fields.sort(key=lambda f: f["field"].lower() != q_lower)

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

    indexes.sort(key=lambda idx: idx["index"].lower() != q_lower)

    return {"tables": tables, "fields": fields, "indexes": indexes}


def _load_table_detail(database_name: str, table_name: str, session: Session):
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


@router.get("/tables/{database_name}/{table_name}")
def table_detail(database_name: str, table_name: str, session: Session = Depends(get_session)):
    return _load_table_detail(database_name, table_name, session)


@router.get("/tables/{database_name}/{table_name}/export")
def export_table(database_name: str, table_name: str, session: Session = Depends(get_session)):
    detail = _load_table_detail(database_name, table_name, session)
    if "error" in detail:
        raise HTTPException(status_code=404, detail=detail["error"])

    workbook = Workbook()
    bold = Font(bold=True)

    fields_sheet = workbook.active
    fields_sheet.title = "Campos"
    fields_sheet.append(["Nome", "Tipo", "Formato", "Tamanho", "Obrigatório", "Label", "Descrição"])
    for cell in fields_sheet[1]:
        cell.font = bold
    for f in detail["fields"]:
        fields_sheet.append(
            [
                f["name"],
                f["data_type"],
                f["format"],
                f["max_width"],
                "sim" if f["mandatory"] else "",
                f["label"],
                f["description"],
            ]
        )
    for column_cells in fields_sheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells if cell.value is not None)
        fields_sheet.column_dimensions[column_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    indexes_sheet = workbook.create_sheet("Índices")
    indexes_sheet.append(["Nome", "Campos", "Único", "Primário"])
    for cell in indexes_sheet[1]:
        cell.font = bold
    for idx in detail["indexes"]:
        indexes_sheet.append(
            [
                idx["name"],
                ", ".join(f"{f['name']}{'' if f['ascending'] else ' DESC'}" for f in idx["fields"]),
                "sim" if idx["is_unique"] else "",
                "sim" if idx["is_primary"] else "",
            ]
        )
    for column_cells in indexes_sheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells if cell.value is not None)
        indexes_sheet.column_dimensions[column_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    filename = f"{detail['database']}.{detail['table']}.xlsx".replace(" ", "_")
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
