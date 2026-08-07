import { useCallback, useEffect, useState } from "react";
import { listDatabases, search, tableDetail } from "./api";
import ImportPanel from "./components/ImportPanel";
import SearchResults from "./components/SearchResults";
import TableDetail from "./components/TableDetail";
import "./App.css";

function App() {
  const [databases, setDatabases] = useState([]);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState(null);

  const refreshDatabases = useCallback(() => {
    listDatabases().then(setDatabases).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    refreshDatabases();
  }, [refreshDatabases]);

  async function handleSearch(event) {
    event.preventDefault();
    if (query.trim().length < 2) return;
    try {
      setError(null);
      const data = await search(query.trim());
      setResults(data);
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleSelectTable(databaseName, tableName) {
    try {
      const data = await tableDetail(databaseName, tableName);
      setDetail(data);
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Datasul DF Explorer</h1>
        <p>Busque tabelas, campos e índices nas bases Progress importadas.</p>
      </header>

      <ImportPanel databases={databases} onChanged={refreshDatabases} />

      <section className="panel">
        <h2>Busca</h2>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="nome da tabela, campo ou índice"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit">Buscar</button>
        </form>
        {error && <p className="status-error">{error}</p>}
        <SearchResults results={results} onSelectTable={handleSelectTable} />
      </section>

      <TableDetail detail={detail} onClose={() => setDetail(null)} />
    </div>
  );
}

export default App;
