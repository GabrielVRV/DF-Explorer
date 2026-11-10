// JSON evita colisão: o nome da base é livre e pode conter ponto, então "a.b"+"c" != "a"+"b.c".
export function tableKey(database, table) {
  return JSON.stringify([database, table]);
}
