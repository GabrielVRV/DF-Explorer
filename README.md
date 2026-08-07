# Datasul DF Explorer

Ferramenta para importar dumps `.df` (Data Dictionary) de bases Progress/Datasul
e buscar tabelas, campos e índices sem precisar abrir cada `.df` na mão.

## Como funciona

1. Você exporta os `.df` das bases pelo Data Dictionary do Progress.
2. Importa cada arquivo pela API, informando um nome pra base (ex: `multi`, `emsfin`).
3. Busca por tabela/campo/índice cruzando todas as bases importadas.

Os `.df` e o banco SQLite gerado ficam em `backend/data/`, que está no `.gitignore` —
nada da estrutura das bases da empresa é versionado.

## Rodando o backend

Requisitos: Python 3.11+

```bash
cd backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt
./.venv/Scripts/uvicorn app.main:app --reload --port 8000
```

A API sobe em `http://localhost:8000`. Docs interativas em `http://localhost:8000/docs`.

### Importando um .df

```bash
curl -X POST http://localhost:8000/databases/import \
  -F "database_name=multi" \
  -F "file=@caminho/para/multi.df"
```

### Buscando

```bash
curl "http://localhost:8000/search?q=cust-num"
```

## Rodando o frontend

```bash
cd frontend
npm install
npm run dev
```

## Estrutura

```
backend/
  app/
    main.py        API FastAPI
    models.py       tabelas do SQLite (Database, Table, TableField, TableIndex, IndexField)
    parser.py       parser dos arquivos .df
    routers/
      databases.py  import/list/delete de bases
      search.py     busca e detalhe de tabela
  data/             .df importados + schema.db (gitignored)
frontend/           app React
```
