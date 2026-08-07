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
            fechar
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
                <td>{f.name}</td>
                <td>{f.data_type}</td>
                <td>{f.format}</td>
                <td>{f.max_width}</td>
                <td>{f.mandatory ? "sim" : ""}</td>
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
                <td>{idx.name}</td>
                <td>{idx.fields.map((f) => `${f.name}${f.ascending ? "" : " ↓"}`).join(", ")}</td>
                <td>{idx.is_unique ? "sim" : ""}</td>
                <td>{idx.is_primary ? "sim" : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
