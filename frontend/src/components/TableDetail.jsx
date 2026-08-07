function YesBadge({ show }) {
  return show ? <span className="badge badge-yes">sim</span> : null;
}

export default function TableDetail({ detail, onClose }) {
  if (!detail) return null;

  if (detail.error) {
    return (
      <div className="detail-overlay" onClick={onClose}>
        <div className="detail-panel" onClick={(e) => e.stopPropagation()}>
          <p>{detail.error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-overlay" onClick={onClose}>
      <div className="detail-panel" onClick={(e) => e.stopPropagation()}>
        <header>
          <h2>
            {detail.database}.{detail.table}
          </h2>
          <button type="button" onClick={onClose}>
            Fechar
          </button>
        </header>
        <p className="area">Área: {detail.area}</p>

        <h3>Campos</h3>
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Tipo</th>
              <th>Formato</th>
              <th>Tamanho</th>
              <th>Obrigatório</th>
              <th>Label</th>
              <th>Descrição</th>
            </tr>
          </thead>
          <tbody>
            {detail.fields.map((f) => (
              <tr key={f.name}>
                <td className="mono">{f.name}</td>
                <td className="type-badge">{f.data_type}</td>
                <td className="type-badge">{f.format}</td>
                <td>{f.max_width}</td>
                <td>
                  <YesBadge show={f.mandatory} />
                </td>
                <td>{f.label}</td>
                <td className="description-cell">{f.description}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <h3>Índices</h3>
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Campos</th>
              <th>Único</th>
              <th>Primário</th>
            </tr>
          </thead>
          <tbody>
            {detail.indexes.map((idx) => (
              <tr key={idx.name}>
                <td className="mono">{idx.name}</td>
                <td className="type-badge">{idx.fields.map((f) => `${f.name}${f.ascending ? "" : " ↓"}`).join(", ")}</td>
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
      </div>
    </div>
  );
}
