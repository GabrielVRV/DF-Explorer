# Datasul DF Explorer

Ferramenta para importar dumps `.df` (Data Dictionary) de bases Progress/Datasul
e buscar tabelas, campos e índices sem precisar abrir cada `.df` na mão.

## Como funciona

1. Você exporta os `.df` das bases pelo Data Dictionary do Progress.
2. Importa cada arquivo pelo app, informando um nome pra base (ex: `multi`, `emsfin`).
3. Busca por tabela/campo/índice cruzando todas as bases importadas, com prioridade
   pra quem bate exato com o que você digitou.

Os `.df` e o banco SQLite gerado ficam fora do repositório (`backend/data/` em modo
desenvolvimento, ou `%APPDATA%\DF Explorer\data` quando rodando o `.exe`) — nada da
estrutura das bases da empresa é versionado.

## Uso no dia a dia (Windows)

Clique duas vezes no atalho **DF Explorer** na Área de Trabalho (ou em
`backend\dist\DF Explorer.exe`). Abre uma janela nativa do app, com ícone e título
próprios — sem navegador, sem terminal, sem depender de Python/Node instalados na
máquina de quem for usar.

## Gerando o executável (`.exe`)

Só precisa ser feito quando o código mudar. Quem for gerar precisa ter **Python 3.11+**
e **Node.js** instalados (com `python` e `npm` no PATH). Depois disso, quem só for
*usar* o `.exe` gerado não precisa de mais nada instalado.

```bash
build.bat
```

Esse script builda o frontend, prepara o `.venv` do backend, instala as dependências
(incluindo o PyInstaller) e gera `backend\dist\DF Explorer.exe` com a logo do projeto
embutida (`Imgs/DF-Explorer-Logo.ico`). Depois é só criar um atalho pra esse `.exe`.

A configuração do build fica em `backend/DF Explorer.spec` (versionado, editável se
precisar ajustar algo do empacotamento).

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
via `frontend/.env.development`. Fora do modo dev (ou dentro do `.exe`), o próprio
backend serve o frontend já compilado (`frontend/dist`) na mesma porta.

Pra testar o app completo sem gerar o `.exe`, rode `start.bat` (sobe tudo via Python
diretamente, mostrando o terminal — útil pra depurar). `stop.bat` encerra.

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
    main.py            API FastAPI + serve o frontend compilado
    models.py           tabelas do SQLite (Database, Table, TableField, TableIndex, IndexField)
    parser.py           parser dos arquivos .df
    routers/
      databases.py      import/list/rename/delete de bases
      search.py         busca e detalhe de tabela
  desktop.py            abre a janela nativa do app (usa pywebview)
  "DF Explorer.spec"    configuracao do build do executavel (PyInstaller)
  data/                 .df importados + schema.db em modo dev (gitignored)
  dist/                 executavel gerado pelo build.bat (gitignored)
frontend/                app React
  dist/                  build de producao servido pelo backend (gitignored, gerado)
Imgs/                    logo/icone do projeto
build.bat                gera o .exe (build.bat)
start.bat                roda o app via Python, sem empacotar (debug)
stop.bat                 encerra o app rodando via start.bat
```
