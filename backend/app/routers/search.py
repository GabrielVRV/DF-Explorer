from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlmodel import Session, select

from app.db import get_session
from app.excel_export import build_multi_table_workbook, build_single_table_workbook
from app.models import Database, Table, TableField, TableIndex, IndexField

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

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


def _xlsx_response(content: bytes, filename: str) -> Response:
    return Response(
        content=content,
        media_type=XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# Declarada antes de /tables/{database_name}/{table_name} para que "export" nunca
# seja interpretado como nome de base, mesmo que o número de segmentos mude.
@router.get("/tables/export")
def export_tables(
    # default_factory evita o 422 do FastAPI: lista ausente cai na validação e vira 400.
    database: list[str] = Query(default_factory=list),
    table: list[str] = Query(default_factory=list),
    session: Session = Depends(get_session),
):
    if not database or len(database) != len(table):
        raise HTTPException(
            status_code=400,
            detail="Informe ao menos uma tabela, com o mesmo número de 'database' e 'table'.",
        )

    # dict.fromkeys remove duplicados preservando a primeira ocorrência.
    pairs = list(dict.fromkeys(zip(database, table)))

    details = []
    for database_name, table_name in pairs:
        detail = _load_table_detail(database_name, table_name, session)
        if "error" in detail:
            raise HTTPException(
                status_code=404,
                detail=f"Tabela não encontrada: {database_name}.{table_name}",
            )
        details.append(detail)

    return _xlsx_response(
        build_multi_table_workbook(details),
        f"df-explorer-{len(details)}-tabelas.xlsx",
    )


@router.get("/tables/{database_name}/{table_name}")
def table_detail(database_name: str, table_name: str, session: Session = Depends(get_session)):
    return _load_table_detail(database_name, table_name, session)


@router.get("/tables/{database_name}/{table_name}/export")
def export_table(database_name: str, table_name: str, session: Session = Depends(get_session)):
    detail = _load_table_detail(database_name, table_name, session)
    if "error" in detail:
        raise HTTPException(status_code=404, detail=detail["error"])

    filename = f"{detail['database']}.{detail['table']}.xlsx".replace(" ", "_")
    return _xlsx_response(build_single_table_workbook(detail), filename)
