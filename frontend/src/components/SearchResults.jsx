import { tableKey } from "../tableKey";

function YesBadge({ show }) {
  return show ? <span className="badge badge-yes">sim</span> : null;
}

export default function SearchResults({
  results,
  filter = "all",
  onSelectTable,
  onCopyField,
  selectedTables = [],
  onToggleTable,
  onSetTablesSelected,
}) {
  if (!results) return null;

  const { tables, fields, indexes } = results;
  const hasResults = tables.length + fields.length + indexes.length > 0;

  if (!hasResults) {
    return <p className="empty">Nenhum resultado encontrado.</p>;
  }

  const selectedKeys = new Set(selectedTables.map((t) => tableKey(t.database, t.table)));
  const selectedVisibleCount = tables.filter((t) => selectedKeys.has(tableKey(t.database, t.table))).length;
  const allVisibleSelected = tables.length > 0 && selectedVisibleCount === tables.length;
  const someVisibleSelected = selectedVisibleCount > 0 && !allVisibleSelected;

  const showTables = filter === "all" || filter === "tables";
  const showFields = filter === "all" || filter === "fields";
  const showIndexes = filter === "all" || filter === "indexes";

  return (
    <div className="results">
      {showTables && tables.length > 0 && (
        <section className="result-card">
          <h3>Tabelas ({tables.length})</h3>
          <table>
            <thead>
              <tr>
                <th className="select-cell">
                  <input
                    type="checkbox"
                    aria-label="Selecionar todas as tabelas desta busca"
                    checked={allVisibleSelected}
                    // indeterminate só existe como propriedade do DOM, não como atributo
                    ref={(el) => {
                      if (el) el.indeterminate = someVisibleSelected;
                    }}
                    onChange={(e) => onSetTablesSelected(tables, e.target.checked)}
                  />
                </th>
                <th>Base</th>
                <th>Tabela</th>
                <th>Área</th>
              </tr>
            </thead>
            <tbody>
              {tables.map((t) => {
                const key = tableKey(t.database, t.table);
                const isSelected = selectedKeys.has(key);
                return (
                  <tr
                    key={key}
                    className={`clickable${isSelected ? " selected" : ""}`}
                    onClick={() => onSelectTable(t.database, t.table)}
                  >
                    <td className="select-cell" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        aria-label={`Selecionar ${t.database}.${t.table}`}
                        checked={isSelected}
                        onChange={() => onToggleTable(t.database, t.table)}
                      />
                    </td>
                    <td className="mono">{t.database}</td>
                    <td className="mono">{t.table}</td>
                    <td>{t.area}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </section>
      )}

      {showFields && fields.length > 0 && (
        <section className="result-card">
          <h3>Campos ({fields.length})</h3>
          <table>
            <thead>
              <tr>
                <th>Base</th>
                <th>Tabela</th>
                <th>Campo</th>
                <th>Tipo</th>
                <th>Formato</th>
                <th>Tamanho</th>
                <th>Obrigatório</th>
              </tr>
            </thead>
            <tbody>
              {fields.map((f) => (
                <tr
                  key={`${f.database}.${f.table}.${f.field}`}
                  className="clickable"
                  onClick={() => onSelectTable(f.database, f.table)}
                >
                  <td className="mono">{f.database}</td>
                  <td className="mono">{f.table}</td>
                  <td
                    className="mono copyable"
                    title="Clique para copiar tabela.campo"
                    onClick={(e) => {
                      e.stopPropagation();
                      onCopyField(f.table, f.field);
                    }}
                  >
                    {f.field}
                  </td>
                  <td className="type-badge">{f.data_type}</td>
                  <td className="type-badge">{f.format}</td>
                  <td>{f.max_width}</td>
                  <td>
                    <YesBadge show={f.mandatory} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {showIndexes && indexes.length > 0 && (
        <section className="result-card">
          <h3>Índices ({indexes.length})</h3>
          <table>
            <thead>
              <tr>
                <th>Base</th>
                <th>Tabela</th>
                <th>Índice</th>
                <th>Campos</th>
                <th>Único</th>
                <th>Primário</th>
              </tr>
            </thead>
            <tbody>
              {indexes.map((idx) => (
                <tr
                  key={`${idx.database}.${idx.table}.${idx.index}`}
                  className="clickable"
                  onClick={() => onSelectTable(idx.database, idx.table)}
                >
                  <td className="mono">{idx.database}</td>
                  <td className="mono">{idx.table}</td>
                  <td className="mono">{idx.index}</td>
                  <td className="type-badge">{idx.fields.map((f) => f.name).join(", ")}</td>
                  <td>
                    <YesBadge show={idx.is_unique} />
                  </td>
                  <td>
                    <YesBadge show={idx.is_primary} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
