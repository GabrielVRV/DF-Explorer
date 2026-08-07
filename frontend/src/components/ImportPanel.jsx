import { useState } from "react";
import { importDatabase, deleteDatabase } from "../api";

export default function ImportPanel({ databases, onChanged }) {
  const [databaseName, setDatabaseName] = useState("");
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!databaseName || !file) return;

    setLoading(true);
    setStatus(null);
    try {
      const result = await importDatabase(databaseName, file);
      setStatus({ ok: true, message: `${result.tables} tabelas, ${result.fields} campos, ${result.indexes} índices importados.` });
      setDatabaseName("");
      setFile(null);
      onChanged();
    } catch (error) {
      setStatus({ ok: false, message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(name) {
    if (!confirm(`Remover a base "${name}" do índice?`)) return;
    await deleteDatabase(name);
    onChanged();
  }

  return (
    <section className="panel">
      <h2>Bases importadas</h2>
      <ul className="database-list">
        {databases.map((db) => (
          <li key={db.name}>
            <span>{db.name}</span>
            <button type="button" onClick={() => handleDelete(db.name)} title="Remover">
              ×
            </button>
          </li>
        ))}
        {databases.length === 0 && <li className="empty">Nenhuma base importada ainda.</li>}
      </ul>

      <form onSubmit={handleSubmit} className="import-form">
        <input
          type="text"
          placeholder="nome da base (ex: multi)"
          value={databaseName}
          onChange={(e) => setDatabaseName(e.target.value)}
        />
        <input type="file" accept=".df" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit" disabled={loading || !databaseName || !file}>
          {loading ? "Importando..." : "Importar .df"}
        </button>
      </form>
      {status && <p className={status.ok ? "status-ok" : "status-error"}>{status.message}</p>}
    </section>
  );
}
