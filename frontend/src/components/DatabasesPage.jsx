import { useState } from "react";
import { importDatabase, deleteDatabase } from "../api";

function nameFromFile(file) {
  return file.name.replace(/\.df$/i, "");
}

export default function DatabasesPage({ databases, onChanged }) {
  const [databaseName, setDatabaseName] = useState("");
  const [files, setFiles] = useState([]);
  const [progress, setProgress] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const isBatch = files.length > 1;

  function handleFileChange(event) {
    const selected = Array.from(event.target.files);
    setFiles(selected);
    if (selected.length === 1 && !databaseName) {
      setDatabaseName(nameFromFile(selected[0]));
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (files.length === 0 || (!isBatch && !databaseName)) return;

    setLoading(true);
    setResults([]);
    const outcomes = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const name = isBatch ? nameFromFile(file) : databaseName;
      setProgress({ index: i + 1, total: files.length, name });
      try {
        const result = await importDatabase(name, file);
        outcomes.push({
          name,
          ok: true,
          message: `${result.tables} tabelas, ${result.fields} campos, ${result.indexes} índices`,
        });
      } catch (error) {
        outcomes.push({ name, ok: false, message: error.message });
      }
    }

    setResults(outcomes);
    setProgress(null);
    setFiles([]);
    setDatabaseName("");
    setLoading(false);
    onChanged();
  }

  async function handleDelete(name) {
    if (!confirm(`Remover a base "${name}" do índice?`)) return;
    await deleteDatabase(name);
    onChanged();
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Bases de dados</h1>
        <p>Gerencie os dumps .df importados e adicione novas bases.</p>
      </div>

      <section className="card">
        <h2>Importadas ({databases.length})</h2>
        {databases.length === 0 ? (
          <p className="empty">Nenhuma base importada ainda.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Arquivo de origem</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {databases.map((db) => (
                <tr key={db.name}>
                  <td className="mono">{db.name}</td>
                  <td className="type-badge">{db.source_file}</td>
                  <td className="actions-cell">
                    <button type="button" className="btn-danger" onClick={() => handleDelete(db.name)}>
                      Remover
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="card">
        <h2>Importar .df</h2>
        <form onSubmit={handleSubmit} className="import-form">
          <input
            type="text"
            placeholder="nome da base (ex: multi)"
            value={databaseName}
            disabled={isBatch}
            onChange={(e) => setDatabaseName(e.target.value)}
          />
          <input type="file" accept=".df" multiple onChange={handleFileChange} />
          <button type="submit" disabled={loading || files.length === 0 || (!isBatch && !databaseName)}>
            {loading ? "Importando..." : files.length > 1 ? `Importar ${files.length} arquivos` : "Importar"}
          </button>
        </form>
        {isBatch && <p className="hint">O nome de cada base será o nome do arquivo, sem a extensão .df.</p>}
        {progress && (
          <p className="hint">
            Importando {progress.index}/{progress.total}: {progress.name}...
          </p>
        )}
        {results.length > 0 && (
          <ul className="import-results">
            {results.map((r) => (
              <li key={r.name} className={r.ok ? "status-ok" : "status-error"}>
                {r.name}: {r.message}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
