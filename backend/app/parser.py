import re
from dataclasses import dataclass, field

CPSTREAM_RE = re.compile(rb"cpstream=([\w-]+)", re.IGNORECASE)

CODEPAGE_ALIASES = {
    "ibm850": "cp850",
    "ibm437": "cp437",
    "iso8859-1": "latin-1",
    "1252": "cp1252",
    "utf-8": "utf-8",
}


def decode_df_bytes(raw: bytes) -> str:
    """Progress dumps declare their codepage in a `cpstream=` trailer line (e.g. ibm850)."""
    match = CPSTREAM_RE.search(raw)
    codec = CODEPAGE_ALIASES.get(match.group(1).decode("ascii").lower(), "cp850") if match else "cp850"
    return raw.decode(codec, errors="replace")


@dataclass
class ParsedField:
    name: str
    table_name: str
    data_type: str = ""
    format: str = ""
    initial: str = ""
    label: str = ""
    column_label: str = ""
    help_text: str = ""
    position: int | None = None
    max_width: int | None = None
    mandatory: bool = False
    description: str = ""


@dataclass
class ParsedIndexField:
    field_name: str
    ascending: bool = True


@dataclass
class ParsedIndex:
    name: str
    table_name: str
    area: str = ""
    is_unique: bool = False
    is_primary: bool = False
    fields: list[ParsedIndexField] = field(default_factory=list)


@dataclass
class ParsedTable:
    name: str
    dump_name: str = ""
    area: str = ""
    description: str = ""


@dataclass
class ParsedSchema:
    tables: list[ParsedTable] = field(default_factory=list)
    fields: list[ParsedField] = field(default_factory=list)
    indexes: list[ParsedIndex] = field(default_factory=list)


QUOTED = r'"([^"]*)"'

TABLE_HEADER_RE = re.compile(r'^ADD TABLE\s+"([^"]+)"')
FIELD_HEADER_RE = re.compile(r'^ADD FIELD\s+"([^"]+)"\s+OF\s+"([^"]+)"\s+AS\s+(\S+)')
INDEX_HEADER_RE = re.compile(r'^ADD INDEX\s+"([^"]+)"\s+ON\s+"([^"]+)"')
INDEX_FIELD_RE = re.compile(r'^INDEX-FIELD\s+"([^"]+)"\s*(ASCENDING|DESCENDING)?', re.IGNORECASE)


def _attr_value(line: str, key: str) -> str | None:
    match = re.match(rf'^{key}\s+"([^"]*)"', line, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.match(rf'^{key}\s+(\S+)', line, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _logical_lines(content: str) -> list[str]:
    """Join physical lines whose quotes span multiple lines (multi-line DESCRIPTION)."""
    logical: list[str] = []
    buffer: list[str] | None = None
    for raw_line in content.splitlines():
        if buffer is None:
            buffer = [raw_line]
        else:
            buffer.append(raw_line)
        if sum(l.count('"') for l in buffer) % 2 == 0:
            logical.append("\n".join(buffer))
            buffer = None
    if buffer is not None:
        logical.append("\n".join(buffer))
    return logical


def _normalize_logical_line(line: str) -> str:
    if "\n" not in line:
        return line.strip()
    first, rest = line.split("\n", 1)
    return f"{first.strip()}\n{rest}"


def _split_blocks(content: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for raw_line in _logical_lines(content):
        line = _normalize_logical_line(raw_line)
        if not line:
            continue
        if line == ".":
            break
        if line.startswith("ADD "):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def parse_df(content: str) -> ParsedSchema:
    schema = ParsedSchema()

    for block in _split_blocks(content):
        header = block[0]
        body = block[1:]

        table_match = TABLE_HEADER_RE.match(header)
        if table_match:
            table = ParsedTable(name=table_match.group(1))
            for line in body:
                value = _attr_value(line, "AREA")
                if value is not None:
                    table.area = value
                value = _attr_value(line, "DUMP-NAME")
                if value is not None:
                    table.dump_name = value
                value = _attr_value(line, "DESCRIPTION")
                if value is not None:
                    table.description = value
            schema.tables.append(table)
            continue

        field_match = FIELD_HEADER_RE.match(header)
        if field_match:
            parsed_field = ParsedField(
                name=field_match.group(1),
                table_name=field_match.group(2),
                data_type=field_match.group(3),
            )
            for line in body:
                if line.upper() == "MANDATORY":
                    parsed_field.mandatory = True
                    continue
                for key, attr in (
                    ("FORMAT", "format"),
                    ("INITIAL", "initial"),
                    ("COLUMN-LABEL", "column_label"),
                    ("LABEL", "label"),
                    ("HELP", "help_text"),
                    ("DESCRIPTION", "description"),
                ):
                    value = _attr_value(line, key)
                    if value is not None:
                        setattr(parsed_field, attr, value)
                        break
                else:
                    value = _attr_value(line, "POSITION")
                    if value is not None and value.isdigit():
                        parsed_field.position = int(value)
                    value = _attr_value(line, "MAX-WIDTH")
                    if value is not None and value.isdigit():
                        parsed_field.max_width = int(value)
            schema.fields.append(parsed_field)
            continue

        index_match = INDEX_HEADER_RE.match(header)
        if index_match:
            parsed_index = ParsedIndex(name=index_match.group(1), table_name=index_match.group(2))
            for line in body:
                upper = line.upper()
                if upper == "UNIQUE":
                    parsed_index.is_unique = True
                    continue
                if upper == "PRIMARY":
                    parsed_index.is_primary = True
                    continue
                index_field_match = INDEX_FIELD_RE.match(line)
                if index_field_match:
                    ascending = (index_field_match.group(2) or "ASCENDING").upper() != "DESCENDING"
                    parsed_index.fields.append(
                        ParsedIndexField(field_name=index_field_match.group(1), ascending=ascending)
                    )
                    continue
                value = _attr_value(line, "AREA")
                if value is not None:
                    parsed_index.area = value
            schema.indexes.append(parsed_index)
            continue

    return schema
