import { tablesExportUrl } from "../api";
import { tableKey } from "../tableKey";

export default function SelectionBar({ selectedTables, onRemove, onClear }) {
  if (selectedTables.length === 0) return null;

  return (
    <section className="selection-bar">
      <div className="selection-header">
        <strong>{selectedTables.length} tabela(s) selecionada(s)</strong>
        <div className="selection-actions">
          <button type="button" className="btn-secondary" onClick={onClear}>
            Limpar seleção
          </button>
          {/* Link GET com download: é assim que o download funciona dentro da janela pywebview */}
          <a className="btn-secondary btn-primary" href={tablesExportUrl(selectedTables)} download>
            Exportar Excel
          </a>
        </div>
      </div>
      <ul className="selection-chips">
        {selectedTables.map(({ database, table }) => (
          <li key={tableKey(database, table)} className="chip">
            <span className="mono">
              {database}.{table}
            </span>
            <button type="button" aria-label={`Remover ${database}.${table} da seleção`} onClick={() => onRemove(database, table)}>
              ×
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
