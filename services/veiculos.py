"""Regras para gerenciamento de veículos."""

import sqlite3

from database.repositories import movimentacoes, vagas, veiculos


TIPOS_VEICULO = {1: "CARRO", 2: "MOTO"}


class ErroVeiculo(ValueError):
    """Erro de regra de negócio relacionado a veículos."""


def listar_veiculos(caminho=None, filtro_placa=""):
    """Lista veículos, com filtro opcional e parcial por placa."""
    filtro_normalizado = (filtro_placa or "").strip().casefold()
    resultado = []
    for veiculo in veiculos.listar(caminho):
        if filtro_normalizado not in veiculo[1].casefold():
            continue
        resultado.append(
            {
                "id": veiculo[0],
                "placa": veiculo[1],
                "modelo": veiculo[2],
                "cor": veiculo[3],
                "tipo": veiculo[4],
                "tipo_nome": TIPOS_VEICULO[veiculo[4]],
            }
        )
    return resultado


def cadastrar_veiculo(placa, modelo, cor, tipo, caminho=None):
    """Cadastra veículo e apresenta duplicidade de placa de forma clara."""
    try:
        return veiculos.criar(placa, modelo, cor, tipo, caminho)
    except sqlite3.IntegrityError as erro:
        raise ErroVeiculo("Já existe um veículo cadastrado com esta placa.") from erro


def atualizar_veiculo(veiculo_id, placa, modelo, cor, tipo, caminho=None):
    """Atualiza veículo sem incompatibilizar uma movimentação aberta."""
    veiculo = veiculos.buscar_por_id(veiculo_id, caminho)
    if veiculo is None:
        raise ErroVeiculo("Veículo não encontrado.")

    movimentacao = movimentacoes.buscar_aberta_para_veiculo(veiculo_id, caminho)
    if movimentacao is not None and not _tipo_compativel_com_movimentacao(
        tipo, movimentacao, caminho
    ):
        raise ErroVeiculo(
            "Não é possível alterar o tipo de um veículo estacionado para um tipo "
            "incompatível com a vaga utilizada."
        )

    try:
        return veiculos.atualizar(
            veiculo_id,
            placa=placa,
            modelo=modelo,
            cor=cor,
            tipo=tipo,
            caminho=caminho,
        )
    except sqlite3.IntegrityError as erro:
        raise ErroVeiculo("Já existe um veículo cadastrado com esta placa.") from erro


def excluir_veiculo(veiculo_id, caminho=None):
    """Exclui apenas veículos sem movimentações abertas ou históricas."""
    veiculo = veiculos.buscar_por_id(veiculo_id, caminho)
    if veiculo is None:
        raise ErroVeiculo("Veículo não encontrado.")
    if movimentacoes.existe_aberta_para_veiculo(veiculo_id, caminho):
        raise ErroVeiculo("Não é possível excluir um veículo que está estacionado.")
    try:
        return veiculos.excluir(veiculo_id, caminho)
    except sqlite3.IntegrityError as erro:
        raise ErroVeiculo(
            "Não é possível excluir um veículo vinculado ao histórico de movimentações."
        ) from erro


def _tipo_compativel_com_movimentacao(tipo_veiculo, movimentacao, caminho):
    vaga = vagas.buscar_por_id(movimentacao[2], caminho)
    tipo_vaga = vaga[2]
    if tipo_veiculo == 2:
        return tipo_vaga == 2
    return tipo_vaga == 1 or (tipo_vaga == 3 and movimentacao[7] == 1)
