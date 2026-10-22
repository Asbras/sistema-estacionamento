"""Consultas básicas de movimentações, sem operações de entrada ou saída."""

from database.repositories._common import (
    consultar_todos,
    consultar_um,
    executar,
)


def buscar_por_id(movimentacao_id, caminho=None, conexao=None):
    return consultar_um(
        "SELECT * FROM movimentacao WHERE id = ?", (movimentacao_id,), caminho,
        conexao,
    )


def listar(caminho=None):
    return consultar_todos(
        "SELECT * FROM movimentacao ORDER BY id", caminho=caminho
    )


def listar_abertas(caminho=None):
    return consultar_todos(
        "SELECT * FROM movimentacao WHERE saida IS NULL ORDER BY id",
        caminho=caminho,
    )


def existe_aberta_para_veiculo(veiculo_id, caminho=None):
    return consultar_um(
        "SELECT 1 FROM movimentacao WHERE veiculo_id = ? AND saida IS NULL LIMIT 1",
        (veiculo_id,), caminho,
    ) is not None


def buscar_aberta_para_veiculo(veiculo_id, caminho=None, conexao=None):
    return consultar_um(
        "SELECT * FROM movimentacao WHERE veiculo_id = ? AND saida IS NULL "
        "ORDER BY id LIMIT 1",
        (veiculo_id,), caminho, conexao,
    )


def criar(veiculo_id, vaga_id, usuario_entrada_id, entrada, pcd,
          caminho=None, conexao=None):
    return executar(
        "INSERT INTO movimentacao "
        "(veiculo_id, vaga_id, usuario_entrada_id, entrada, saida, "
        "usuario_saida_id, pcd, valor) VALUES (?, ?, ?, ?, NULL, NULL, ?, NULL)",
        (veiculo_id, vaga_id, usuario_entrada_id, entrada, pcd),
        caminho, retornar_id=True, conexao=conexao,
    )


def encerrar(movimentacao_id, usuario_saida_id, saida, valor,
             caminho=None, conexao=None):
    return executar(
        "UPDATE movimentacao SET usuario_saida_id = ?, saida = ?, valor = ? "
        "WHERE id = ? AND saida IS NULL",
        (usuario_saida_id, saida, valor, movimentacao_id), caminho,
        conexao=conexao,
    )


def existe_aberta_para_vaga(vaga_id, caminho=None):
    return consultar_um(
        "SELECT 1 FROM movimentacao WHERE vaga_id = ? AND saida IS NULL LIMIT 1",
        (vaga_id,), caminho,
    ) is not None
