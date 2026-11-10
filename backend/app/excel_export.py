"""Geração dos arquivos .xlsx de exportação (uma tabela ou várias).

Módulo puro: recebe os dicionários montados por `_load_table_detail` e devolve bytes,
sem depender de FastAPI nem de SQLModel.
"""

from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.worksheet import Worksheet

TableDetail = dict[str, Any]

EXCEL_SHEET_NAME_MAX_LENGTH = 31
# O Excel rejeita estes caracteres em nomes de aba.
EXCEL_FORBIDDEN_SHEET_CHARS = "[]:*?/\\"
SHEET_NAME_REPLACEMENT = "_"
SHEET_NAME_COLLISION_MARK = "~"

COLUMN_MIN_WIDTH = 10
COLUMN_MAX_WIDTH = 60
COLUMN_WIDTH_PADDING = 2

YES_TEXT = "sim"

FIELDS_SHEET_NAME = "Campos"
INDEXES_SHEET_NAME = "Índices"
SUMMARY_SHEET_NAME = "Tabelas"
# "History" é nome reservado do Excel.
EXCEL_RESERVED_SHEET_NAME = "History"
DEFAULT_SHEET_NAME = "Tabela"
SHEET_NAME_FORBIDDEN_EDGE_CHAR = "'"

FIELDS_HEADER = ["Nome", "Tipo", "Formato", "Tamanho", "Obrigatório", "Label", "Descrição"]
INDEXES_HEADER = ["Nome", "Campos", "Único", "Primário"]
SUMMARY_HEADER = ["Base", "Tabela", "Área", "Aba"]

DATABASE_LABEL = "Base"
TABLE_LABEL = "Tabela"
AREA_LABEL = "Área"
FIELDS_TITLE = "CAMPOS"
INDEXES_TITLE = "ÍNDICES"


def _bold_row(sheet: Worksheet, row_number: int) -> None:
    for cell in sheet[row_number]:
        cell.font = Font(bold=True)


def _append_bold_row(sheet: Worksheet, values: list[Any]) -> None:
    sheet.append(values)
    _bold_row(sheet, sheet.max_row)


def _fit_column_widths(sheet: Worksheet) -> None:
    for column_cells in sheet.columns:
        length = max((len(str(cell.value)) for cell in column_cells if cell.value is not None), default=0)
        width = min(max(length + COLUMN_WIDTH_PADDING, COLUMN_MIN_WIDTH), COLUMN_MAX_WIDTH)
        sheet.column_dimensions[column_cells[0].column_letter].width = width


def _yes_or_empty(flag: bool) -> str:
    return YES_TEXT if flag else ""


def _field_row(field: TableDetail) -> list[Any]:
    return [
        field["name"],
        field["data_type"],
        field["format"],
        field["max_width"],
        _yes_or_empty(field["mandatory"]),
        field["label"],
        field["description"],
    ]


def _index_fields_text(index: TableDetail) -> str:
    return ", ".join(f"{f['name']}{'' if f['ascending'] else ' DESC'}" for f in index["fields"])


def _index_row(index: TableDetail) -> list[Any]:
    return [
        index["name"],
        _index_fields_text(index),
        _yes_or_empty(index["is_unique"]),
        _yes_or_empty(index["is_primary"]),
    ]


def _to_bytes(workbook: Workbook) -> bytes:
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def build_single_table_workbook(detail: TableDetail) -> bytes:
    workbook = Workbook()

    fields_sheet = workbook.active
    assert fields_sheet is not None  # Workbook() sempre cria a aba ativa
    fields_sheet.title = FIELDS_SHEET_NAME
    _append_bold_row(fields_sheet, FIELDS_HEADER)
    for field in detail["fields"]:
        fields_sheet.append(_field_row(field))
    _fit_column_widths(fields_sheet)

    indexes_sheet = workbook.create_sheet(INDEXES_SHEET_NAME)
    _append_bold_row(indexes_sheet, INDEXES_HEADER)
    for index in detail["indexes"]:
        indexes_sheet.append(_index_row(index))
    _fit_column_widths(indexes_sheet)

    return _to_bytes(workbook)


def _sanitize_sheet_name(name: str) -> str:
    for char in EXCEL_FORBIDDEN_SHEET_CHARS:
        name = name.replace(char, SHEET_NAME_REPLACEMENT)
    return _strip_edge_quotes(name[:EXCEL_SHEET_NAME_MAX_LENGTH]) or DEFAULT_SHEET_NAME


def _strip_edge_quotes(name: str) -> str:
    # O Excel não aceita apóstrofo no início nem no fim do nome da aba.
    return name.strip(SHEET_NAME_FORBIDDEN_EDGE_CHAR)


def _unique_sheet_name(name: str, used_lower: set[str]) -> str:
    candidate = name
    counter = 2
    while candidate.lower() in used_lower:
        suffix = f"{SHEET_NAME_COLLISION_MARK}{counter}"
        candidate = _strip_edge_quotes(name[: EXCEL_SHEET_NAME_MAX_LENGTH - len(suffix)]) + suffix
        counter += 1
    return candidate


def build_sheet_names(details: list[TableDetail]) -> list[str]:
    """Nomes das abas, na ordem recebida.

    Usa só o nome da tabela; se o mesmo nome existir em mais de uma base da seleção,
    usa `base.tabela` para todas essas. A unicidade ignora maiúsculas/minúsculas,
    como o Excel, e considera reservados o nome da aba de resumo e o "History".
    """
    table_counts: dict[str, int] = {}
    for detail in details:
        key = detail["table"].lower()
        table_counts[key] = table_counts.get(key, 0) + 1

    used_lower = {SUMMARY_SHEET_NAME.lower(), EXCEL_RESERVED_SHEET_NAME.lower()}
    names: list[str] = []
    for detail in details:
        is_repeated = table_counts[detail["table"].lower()] > 1
        raw_name = f"{detail['database']}.{detail['table']}" if is_repeated else detail["table"]
        name = _unique_sheet_name(_sanitize_sheet_name(raw_name), used_lower)
        used_lower.add(name.lower())
        names.append(name)
    return names


def _fill_table_sheet(sheet: Worksheet, detail: TableDetail) -> None:
    for label, key in ((DATABASE_LABEL, "database"), (TABLE_LABEL, "table"), (AREA_LABEL, "area")):
        sheet.append([label, detail[key]])
        sheet.cell(row=sheet.max_row, column=1).font = Font(bold=True)

    sheet.append([])
    _append_bold_row(sheet, [FIELDS_TITLE])
    _append_bold_row(sheet, FIELDS_HEADER)
    for field in detail["fields"]:
        sheet.append(_field_row(field))

    sheet.append([])
    _append_bold_row(sheet, [INDEXES_TITLE])
    _append_bold_row(sheet, INDEXES_HEADER)
    for index in detail["indexes"]:
        sheet.append(_index_row(index))

    _fit_column_widths(sheet)


def build_multi_table_workbook(details: list[TableDetail]) -> bytes:
    workbook = Workbook()
    sheet_names = build_sheet_names(details)

    summary_sheet = workbook.active
    assert summary_sheet is not None  # Workbook() sempre cria a aba ativa
    summary_sheet.title = SUMMARY_SHEET_NAME
    _append_bold_row(summary_sheet, SUMMARY_HEADER)
    for detail, sheet_name in zip(details, sheet_names):
        summary_sheet.append([detail["database"], detail["table"], detail["area"], sheet_name])
    _fit_column_widths(summary_sheet)

    for detail, sheet_name in zip(details, sheet_names):
        _fill_table_sheet(workbook.create_sheet(sheet_name), detail)

    return _to_bytes(workbook)
