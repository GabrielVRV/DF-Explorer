import { useEffect, useState } from "react";
import SearchResults from "./SearchResults";

const FILTERS = [
  { key: "all", label: "Tudo" },
  { key: "tables", label: "Tabelas" },
  { key: "fields", label: "Campos" },
  { key: "indexes", label: "Índices" },
];

export default function SearchView({ query, setQuery, onSearch, onClear, searching, error, results, onSelectTable }) {
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    setFilter("all");
  }, [results]);

  return (
    <div className="page">
      <form onSubmit={onSearch} className="search-hero">
        <svg className="search-icon" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
          <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" strokeWidth="2" />
          <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
        <input
          type="text"
          placeholder="Buscar tabela, campo ou índice..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
        />
        {query.length > 0 && (
          <button type="button" className="clear-search" onClick={onClear} title="Limpar busca">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.4">
              <line x1="5" y1="5" x2="19" y2="19" strokeLinecap="round" />
              <line x1="19" y1="5" x2="5" y2="19" strokeLinecap="round" />
            </svg>
          </button>
        )}
        <button type="submit" disabled={searching}>
          {searching ? "Buscando..." : "Buscar"}
        </button>
      </form>

      {error && <p className="status-error banner">{error}</p>}

      {results && (
        <div className="result-tabs">
          {FILTERS.map(({ key, label }) => {
            const count = key === "all" ? results.tables.length + results.fields.length + results.indexes.length : results[key].length;
            if (key !== "all" && count === 0) return null;
            return (
              <button key={key} type="button" className={filter === key ? "active" : ""} onClick={() => setFilter(key)}>
                {label} <span className="count">{count}</span>
              </button>
            );
          })}
        </div>
      )}

      <SearchResults results={results} filter={filter} onSelectTable={onSelectTable} />
    </div>
  );
}
