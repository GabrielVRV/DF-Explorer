# Datasul DF Explorer

Ferramenta para importar dumps `.df` (Data Dictionary) de bases Progress/Datasul
e buscar tabelas, campos e índices sem precisar abrir cada `.df` na mão.

## Como funciona

1. Você exporta os `.df` das bases pelo Data Dictionary do Progress.
2. Importa cada arquivo pelo app, informando um nome pra base (ex: `multi`, `emsfin`).
3. Busca por tabela/campo/índice cruzando todas as bases importadas, com prioridade
   pra quem bate exato com o que você digitou.

Os `.df` e o banco SQLite gerado ficam em `backend/data/`, que está no `.gitignore` —
nada da estrutura das bases da empresa é versionado.

## Uso no dia a dia (Windows)

Clique duas vezes no atalho **DF Explorer** na Área de Trabalho. Ele abre uma janela
própria do app (sem navegador, sem terminal aparecendo) já com tudo funcionando.

Na primeira vez que alguém roda isso numa máquina nova, o próprio atalho cuida de:
- criar o ambiente virtual Python (`.venv`) e instalar as dependências do backend;
- instalar as dependências do frontend e gerar o build de produção.

Isso leva um tempo (1–2 minutos) só na primeira execução; das próximas vezes abre na hora.

**Pré-requisitos na máquina** (só isso precisa estar instalado antes): Python 3.11+ e
Node.js, ambos com `python` e `npm`/`node` acessíveis no PATH do Windows.

Se o atalho não existir ainda numa máquina nova, crie um apontando para
`start_silent.vbs` (ou rode `start.bat` diretamente, que faz a mesma coisa mostrando
o terminal — útil pra depurar se algo falhar). Logs de erro da inicialização silenciosa
vão para `desktop.log` na raiz do projeto.

Para parar os processos manualmente, rode `stop.bat`.

## Rodando em modo desenvolvimento

Pra mexer no código com hot-reload, backend e frontend rodam separados:

```bash
cd backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt
./.venv/Scripts/uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

O frontend em dev mode (`npm run dev`, porta 5173) aponta pra API em `localhost:8000`
via `frontend/.env.development`. Fora do modo dev, o próprio backend serve o frontend
já compilado (`frontend/dist`) na mesma porta — é isso que `desktop.py` usa.

### Importando um .df (via API, sem passar pela tela)

```bash
curl -X POST http://localhost:8000/databases/import \
  -F "database_name=multi" \
  -F "file=@caminho/para/multi.df"
```

### Buscando

```bash
curl "http://localhost:8000/search?q=cust-num"
```

## Estrutura

```
backend/
  app/
    main.py        API FastAPI + serve o frontend compilado
    models.py       tabelas do SQLite (Database, Table, TableField, TableIndex, IndexField)
    parser.py       parser dos arquivos .df
    routers/
      databases.py  import/list/rename/delete de bases
      search.py     busca e detalhe de tabela
  desktop.py        abre a janela nativa do app (usa pywebview)
  data/             .df importados + schema.db (gitignored)
frontend/           app React
  dist/             build de produção servido pelo backend (gitignored, gerado)
start.bat           inicia o app mostrando o terminal (debug)
start_silent.vbs     inicia o app sem nenhuma janela (usado pelo atalho)
stop.bat            encerra o app
```
