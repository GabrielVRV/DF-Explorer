import { useCallback, useEffect, useRef, useState } from "react";
import { listDatabases, search, tableDetail } from "./api";
import DatabasesPage from "./components/DatabasesPage";
import SearchView from "./components/SearchView";
import TableDetail from "./components/TableDetail";
import "./App.css";

function getInitialTheme() {
  const stored = localStorage.getItem("df-explorer-theme");
  if (stored === "light" || stored === "dark") return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function ThemeToggle({ theme, onToggle }) {
  return (
    <button type="button" className="theme-toggle" onClick={onToggle} title="Alternar tema">
      {theme === "dark" ? (
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="4.5" />
          <path d="M12 2.5v2M12 19.5v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M2.5 12h2M19.5 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" strokeLinecap="round" />
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z" strokeLinejoin="round" />
        </svg>
      )}
    </button>
  );
}

function App() {
  const [view, setView] = useState("search");
  const [theme, setTheme] = useState(getInitialTheme);
  const [databases, setDatabases] = useState([]);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState(null);
  const [searching, setSearching] = useState(false);
  const [toast, setToast] = useState(null);
  const toastTimeout = useRef(null);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("df-explorer-theme", theme);
  }, [theme]);

  const refreshDatabases = useCallback(() => {
    listDatabases().then(setDatabases).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    refreshDatabases();
  }, [refreshDatabases]);

  async function handleSearch(event) {
    event.preventDefault();
    if (query.trim().length < 2) return;
    setSearching(true);
    try {
      setError(null);
      const data = await search(query.trim());
      setResults(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setSearching(false);
    }
  }

  function handleClearSearch() {
    setQuery("");
    setResults(null);
    setError(null);
  }

  const copyField = useCallback((tableName, fieldName) => {
    const text = `${tableName}.${fieldName}`;
    navigator.clipboard
      .writeText(text)
      .then(() => setToast({ text, ok: true }))
      .catch(() => setToast({ text: "Não foi possível copiar", ok: false }));
    if (toastTimeout.current) clearTimeout(toastTimeout.current);
    toastTimeout.current = setTimeout(() => setToast(null), 1800);
  }, []);

  async function handleSelectTable(databaseName, tableName) {
    try {
      const data = await tableDetail(databaseName, tableName);
      setDetail(data);
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">DF</span>
          <div>
            <h1>DF Explorer</h1>
            <p>Datasul / Progress</p>
          </div>
        </div>

        <nav className="tabs">
          <button type="button" className={view === "search" ? "active" : ""} onClick={() => setView("search")}>
            Buscar
          </button>
          <button type="button" className={view === "databases" ? "active" : ""} onClick={() => setView("databases")}>
            Bases {databases.length > 0 && <span className="count">{databases.length}</span>}
          </button>
        </nav>

        <ThemeToggle theme={theme} onToggle={() => setTheme((t) => (t === "dark" ? "light" : "dark"))} />
      </header>

      <main className="content">
        {view === "search" ? (
          <SearchView
            query={query}
            setQuery={setQuery}
            onSearch={handleSearch}
            onClear={handleClearSearch}
            searching={searching}
            error={error}
            results={results}
            onSelectTable={handleSelectTable}
            onCopyField={copyField}
          />
        ) : (
          <DatabasesPage databases={databases} onChanged={refreshDatabases} />
        )}
      </main>

      <TableDetail detail={detail} onClose={() => setDetail(null)} onCopyField={copyField} />

      {toast && <div className={`toast ${toast.ok ? "" : "toast-error"}`}>{toast.ok ? "Copiado: " : ""}{toast.text}</div>}
    </div>
  );
}

export default App;
