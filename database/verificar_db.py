"""Verificação isolada do esquema e das restrições básicas do SQLite."""

import sqlite3
import tempfile
from pathlib import Path

from database.connection import conectar
from database.init_db import inicializar_banco


TABELAS_ESPERADAS = {"usuario", "veiculo", "vaga", "movimentacao"}


def verificar():
    """Cria um banco temporário, inicializa duas vezes e valida o esquema."""
    with tempfile.TemporaryDirectory() as diretorio:
        caminho = Path(diretorio) / "estacionamento.db"
        inicializar_banco(caminho)
        inicializar_banco(caminho)

        conexao = conectar(caminho)
        try:
            tabelas = {
                linha[0]
                for linha in conexao.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
                )
            }
            assert tabelas == TABELAS_ESPERADAS, tabelas
            assert conexao.execute("PRAGMA foreign_keys").fetchone()[0] == 1

            colunas = {
                tabela: {
                    linha[1]: {
                        "notnull": linha[3],
                        "default": linha[4],
                        "pk": linha[5],
                    }
                    for linha in conexao.execute(f"PRAGMA table_info({tabela})")
                }
                for tabela in TABELAS_ESPERADAS
            }
            assert colunas["usuario"]["id"]["pk"] == 1
            assert colunas["usuario"]["ativo"]["default"] == "1"
            assert colunas["movimentacao"]["usuario_saida_id"]["notnull"] == 0
            assert colunas["movimentacao"]["saida"]["notnull"] == 0
            assert colunas["movimentacao"]["valor"]["notnull"] == 0
            assert "ocupada" not in colunas["vaga"]

            fks = {
                linha[3]: (linha[2], linha[4], linha[6])
                for linha in conexao.execute("PRAGMA foreign_key_list(movimentacao)")
            }
            assert fks == {
                "veiculo_id": ("veiculo", "id", "RESTRICT"),
                "vaga_id": ("vaga", "id", "RESTRICT"),
                "usuario_entrada_id": ("usuario", "id", "RESTRICT"),
                "usuario_saida_id": ("usuario", "id", "RESTRICT"),
            }, fks

            assert _rejeita(conexao, "INSERT INTO usuario (username, senha, ativo) VALUES ('u', 's', 2)")
            assert _rejeita(conexao, "INSERT INTO veiculo (placa, modelo, cor, tipo) VALUES ('A', 'M', 'C', 3)")
            assert _rejeita(conexao, "INSERT INTO vaga (numero, tipo) VALUES ('1', 4)")
            assert _rejeita(conexao, "INSERT INTO movimentacao (veiculo_id, vaga_id, usuario_entrada_id, entrada, pcd) VALUES (99, 99, 99, 'agora', 0)")
        finally:
            conexao.close()

    print("Verificação concluída: tabelas, idempotência e restrições básicas OK.")


def _rejeita(conexao, sql):
    try:
        conexao.execute(sql)
    except sqlite3.IntegrityError:
        conexao.rollback()
        return True
    conexao.rollback()
    return False


if __name__ == "__main__":
    verificar()
