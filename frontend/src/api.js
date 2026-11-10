const API_URL = import.meta.env.VITE_API_URL || "";

async function handleResponse(response) {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Erro ${response.status}`);
  }
  return response.json();
}

export function listDatabases() {
  return fetch(`${API_URL}/databases`).then(handleResponse);
}

export function search(query) {
  const params = new URLSearchParams({ q: query });
  return fetch(`${API_URL}/search?${params}`).then(handleResponse);
}

export function tableDetail(databaseName, tableName) {
  return fetch(`${API_URL}/search/tables/${encodeURIComponent(databaseName)}/${encodeURIComponent(tableName)}`).then(
    handleResponse
  );
}

export function tableExportUrl(databaseName, tableName) {
  return `${API_URL}/search/tables/${encodeURIComponent(databaseName)}/${encodeURIComponent(tableName)}/export`;
}

// Parâmetros repetidos e pareados: a ordem vira a ordem das abas no Excel.
export function tablesExportUrl(tables) {
  const params = new URLSearchParams();
  tables.forEach(({ database, table }) => {
    params.append("database", database);
    params.append("table", table);
  });
  return `${API_URL}/search/tables/export?${params}`;
}

export function importDatabase(databaseName, file) {
  const formData = new FormData();
  formData.append("database_name", databaseName);
  formData.append("file", file);
  return fetch(`${API_URL}/databases/import`, { method: "POST", body: formData }).then(handleResponse);
}

export function deleteDatabase(databaseName) {
  return fetch(`${API_URL}/databases/${encodeURIComponent(databaseName)}`, { method: "DELETE" }).then(
    handleResponse
  );
}
