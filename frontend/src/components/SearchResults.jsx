export default function SearchResults({ results, onSelectTable }) {
  if (!results) return null;

  const { tables, fields, indexes } = results;
  const hasResults = tables.length + fields.length + indexes.length > 0;

  if (!hasResults) {
    return <p className="empty">Nenhum resultado encontrado.</p>;
  }

  return (
    <div className="results">
      {tables.length > 0 && (
        <section>
          <h3>Tabelas ({tables.length})</h3>
          <table>
            <thead>
              <tr>
                <th>Base</th>
                <th>Tabela</th>
                <th>Área</th>
              </tr>
            </thead>
            <tbody>
              {tables.map((t) => (
                <tr key={`${t.database}.${t.table}`} className="clickable" onClick={() => onSelectTable(t.database, t.table)}>
                  <td>{t.database}</td>
                  <td>{t.table}</td>
                  <td>{t.area}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {fields.length > 0 && (
        <section>
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
                  <td>{f.database}</td>
                  <td>{f.table}</td>
                  <td>{f.field}</td>
                  <td>{f.data_type}</td>
                  <td>{f.format}</td>
                  <td>{f.max_width}</td>
                  <td>{f.mandatory ? "sim" : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {indexes.length > 0 && (
        <section>
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
                  <td>{idx.database}</td>
                  <td>{idx.table}</td>
                  <td>{idx.index}</td>
                  <td>{idx.fields.map((f) => f.name).join(", ")}</td>
                  <td>{idx.is_unique ? "sim" : ""}</td>
                  <td>{idx.is_primary ? "sim" : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
