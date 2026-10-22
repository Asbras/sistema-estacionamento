"""Consultas básicas de movimentações, sem operações de entrada ou saída."""

from database.repositories._common import consultar_todos, consultar_um


def buscar_por_id(movimentacao_id, caminho=None):
    return consultar_um(
        "SELECT * FROM movimentacao WHERE id = ?", (movimentacao_id,), caminho
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


def existe_aberta_para_vaga(vaga_id, caminho=None):
    return consultar_um(
        "SELECT 1 FROM movimentacao WHERE vaga_id = ? AND saida IS NULL LIMIT 1",
        (vaga_id,), caminho,
    ) is not None
