from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select

from app.db import get_session
from app.models import Database, Table, TableField, TableIndex, IndexField
from app.parser import decode_df_bytes, parse_df

router = APIRouter(prefix="/databases", tags=["databases"])


@router.get("")
def list_databases(session: Session = Depends(get_session)):
    return session.exec(select(Database)).all()


@router.post("/import")
async def import_database(
    database_name: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    content = decode_df_bytes(await file.read())
    schema = parse_df(content)

    if not schema.tables:
        raise HTTPException(status_code=400, detail="Nenhuma tabela encontrada no arquivo .df")

    existing = session.exec(select(Database).where(Database.name == database_name)).first()
    if existing:
        _delete_database_data(session, existing.id)
        existing.source_file = file.filename or ""
        db_record = existing
    else:
        db_record = Database(name=database_name, source_file=file.filename or "")
        session.add(db_record)
    session.flush()

    table_ids_by_name: dict[str, int] = {}
    for parsed_table in schema.tables:
        table_record = Table(
            database_id=db_record.id,
            name=parsed_table.name,
            dump_name=parsed_table.dump_name,
            area=parsed_table.area,
            description=parsed_table.description,
        )
        session.add(table_record)
        session.flush()
        table_ids_by_name[parsed_table.name] = table_record.id

    for parsed_field in schema.fields:
        table_id = table_ids_by_name.get(parsed_field.table_name)
        if table_id is None:
            continue
        session.add(
            TableField(
                table_id=table_id,
                name=parsed_field.name,
                data_type=parsed_field.data_type,
                format=parsed_field.format,
                initial=parsed_field.initial,
                label=parsed_field.label,
                column_label=parsed_field.column_label,
                help_text=parsed_field.help_text,
                position=parsed_field.position,
                max_width=parsed_field.max_width,
                mandatory=parsed_field.mandatory,
                description=parsed_field.description,
            )
        )

    for parsed_index in schema.indexes:
        table_id = table_ids_by_name.get(parsed_index.table_name)
        if table_id is None:
            continue
        index_record = TableIndex(
            table_id=table_id,
            name=parsed_index.name,
            area=parsed_index.area,
            is_unique=parsed_index.is_unique,
            is_primary=parsed_index.is_primary,
        )
        session.add(index_record)
        session.flush()
        for position, parsed_index_field in enumerate(parsed_index.fields):
            session.add(
                IndexField(
                    index_id=index_record.id,
                    field_name=parsed_index_field.field_name,
                    ascending=parsed_index_field.ascending,
                    position=position,
                )
            )

    session.commit()

    return {
        "database": database_name,
        "tables": len(schema.tables),
        "fields": len(schema.fields),
        "indexes": len(schema.indexes),
    }


@router.delete("/{database_name}")
def delete_database(database_name: str, session: Session = Depends(get_session)):
    db_record = session.exec(select(Database).where(Database.name == database_name)).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Base nao encontrada")
    _delete_database_data(session, db_record.id)
    session.delete(db_record)
    session.commit()
    return {"deleted": database_name}


def _delete_database_data(session: Session, database_id: int) -> None:
    tables = session.exec(select(Table).where(Table.database_id == database_id)).all()
    for table in tables:
        indexes = session.exec(select(TableIndex).where(TableIndex.table_id == table.id)).all()
        for index in indexes:
            index_fields = session.exec(select(IndexField).where(IndexField.index_id == index.id)).all()
            for index_field in index_fields:
                session.delete(index_field)
            session.delete(index)
        fields = session.exec(select(TableField).where(TableField.table_id == table.id)).all()
        for table_field in fields:
            session.delete(table_field)
        session.delete(table)
    session.commit()
