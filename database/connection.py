"""Criação de conexões SQLite com integridade referencial habilitada."""

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "estacionamento.db"


def conectar(caminho=DEFAULT_DATABASE_PATH):
    """Abre o banco indicado e habilita as chaves estrangeiras na conexão."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao
