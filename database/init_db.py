"""Inicialização idempotente do esquema SQLite do estacionamento."""

from database.connection import DEFAULT_DATABASE_PATH, conectar


SCHEMA = """
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS veiculo (
    id INTEGER PRIMARY KEY,
    placa TEXT NOT NULL UNIQUE,
    modelo TEXT NOT NULL,
    cor TEXT NOT NULL,
    tipo INTEGER NOT NULL CHECK (tipo IN (1, 2))
);

CREATE TABLE IF NOT EXISTS vaga (
    id INTEGER PRIMARY KEY,
    numero TEXT NOT NULL UNIQUE,
    tipo INTEGER NOT NULL CHECK (tipo IN (1, 2, 3))
);

CREATE TABLE IF NOT EXISTS movimentacao (
    id INTEGER PRIMARY KEY,
    veiculo_id INTEGER NOT NULL,
    vaga_id INTEGER NOT NULL,
    usuario_entrada_id INTEGER NOT NULL,
    usuario_saida_id INTEGER,
    entrada TEXT NOT NULL,
    saida TEXT,
    pcd INTEGER NOT NULL CHECK (pcd IN (0, 1)),
    valor REAL,
    FOREIGN KEY (veiculo_id) REFERENCES veiculo (id) ON DELETE RESTRICT,
    FOREIGN KEY (vaga_id) REFERENCES vaga (id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_entrada_id) REFERENCES usuario (id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_saida_id) REFERENCES usuario (id) ON DELETE RESTRICT
);
"""


def inicializar_banco(caminho=DEFAULT_DATABASE_PATH):
    """Cria as tabelas ausentes e retorna o caminho do banco inicializado."""
    conexao = conectar(caminho)
    try:
        conexao.executescript(SCHEMA)
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
    return caminho


if __name__ == "__main__":
    caminho = inicializar_banco()
    print(f"Banco inicializado em: {caminho}")
