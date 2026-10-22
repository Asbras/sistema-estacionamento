"""Acesso a dados de veículos."""

from database.repositories._common import (
    consultar_todos,
    consultar_um,
    executar,
    validar_categoria,
    validar_texto_obrigatorio,
)


def _validar(placa, modelo, cor, tipo):
    validar_texto_obrigatorio("placa", placa)
    validar_texto_obrigatorio("modelo", modelo)
    validar_texto_obrigatorio("cor", cor)
    validar_categoria("tipo", tipo, (1, 2))


def criar(placa, modelo, cor, tipo, caminho=None, conexao=None):
    _validar(placa, modelo, cor, tipo)
    return executar(
        "INSERT INTO veiculo (placa, modelo, cor, tipo) VALUES (?, ?, ?, ?)",
        (placa, modelo, cor, tipo), caminho, retornar_id=True, conexao=conexao,
    )


def buscar_por_id(veiculo_id, caminho=None):
    return consultar_um("SELECT * FROM veiculo WHERE id = ?", (veiculo_id,), caminho)


def buscar_por_placa(placa, caminho=None, conexao=None):
    return consultar_um(
        "SELECT * FROM veiculo WHERE placa = ?", (placa,), caminho, conexao
    )


def listar(caminho=None):
    return consultar_todos("SELECT * FROM veiculo ORDER BY id", caminho=caminho)


def atualizar(veiculo_id, placa=None, modelo=None, cor=None, tipo=None, caminho=None):
    alteracoes = []
    parametros = []
    campos = (("placa", placa), ("modelo", modelo), ("cor", cor))
    for campo, valor in campos:
        if valor is not None:
            validar_texto_obrigatorio(campo, valor)
            alteracoes.append(f"{campo} = ?")
            parametros.append(valor)
    if tipo is not None:
        validar_categoria("tipo", tipo, (1, 2))
        alteracoes.append("tipo = ?")
        parametros.append(tipo)
    if not alteracoes:
        raise ValueError("Informe ao menos um campo para atualizar.")
    parametros.append(veiculo_id)
    return executar(
        f"UPDATE veiculo SET {', '.join(alteracoes)} WHERE id = ?",
        parametros, caminho,
    )


def excluir(veiculo_id, caminho=None):
    return executar("DELETE FROM veiculo WHERE id = ?", (veiculo_id,), caminho)
