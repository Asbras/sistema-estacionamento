"""Regras para gerenciamento de vagas do estacionamento."""

import sqlite3

from database.repositories import movimentacoes, vagas, veiculos


TIPOS_VAGA = {1: "CARRO", 2: "MOTO", 3: "PCD"}


class ErroVaga(ValueError):
    """Erro de regra de negócio relacionado a vagas."""


def listar_vagas(caminho=None):
    """Lista vagas com a situação derivada de movimentações abertas."""
    resultado = []
    for vaga in vagas.listar(caminho):
        ocupada = movimentacoes.existe_aberta_para_vaga(vaga[0], caminho)
        resultado.append(
            {
                "id": vaga[0],
                "numero": vaga[1],
                "tipo": vaga[2],
                "tipo_nome": TIPOS_VAGA[vaga[2]],
                "situacao": "OCUPADA" if ocupada else "LIVRE",
            }
        )
    return resultado


def cadastrar_vaga(numero, tipo, caminho=None):
    """Cadastra uma vaga e traduz duplicidade para um erro compreensível."""
    try:
        return vagas.criar(numero, tipo, caminho)
    except sqlite3.IntegrityError as erro:
        raise ErroVaga("Já existe uma vaga cadastrada com este número.") from erro


def atualizar_vaga(vaga_id, numero, tipo, caminho=None):
    """Atualiza uma vaga sem tornar incompatível a movimentação aberta atual."""
    vaga = vagas.buscar_por_id(vaga_id, caminho)
    if vaga is None:
        raise ErroVaga("Vaga não encontrada.")

    movimentacao = movimentacoes.buscar_aberta_para_vaga(vaga_id, caminho)
    if movimentacao is not None and not _tipo_compativel_com_movimentacao(
        tipo, movimentacao, caminho
    ):
        raise ErroVaga(
            "Não é possível alterar o tipo de uma vaga ocupada para um tipo "
            "incompatível com o veículo estacionado."
        )

    try:
        return vagas.atualizar(vaga_id, numero=numero, tipo=tipo, caminho=caminho)
    except sqlite3.IntegrityError as erro:
        raise ErroVaga("Já existe uma vaga cadastrada com este número.") from erro


def excluir_vaga(vaga_id, caminho=None):
    """Exclui uma vaga livre que ainda não possua histórico associado."""
    vaga = vagas.buscar_por_id(vaga_id, caminho)
    if vaga is None:
        raise ErroVaga("Vaga não encontrada.")
    if movimentacoes.existe_aberta_para_vaga(vaga_id, caminho):
        raise ErroVaga("Não é possível excluir uma vaga que está ocupada.")
    try:
        return vagas.excluir(vaga_id, caminho)
    except sqlite3.IntegrityError as erro:
        raise ErroVaga(
            "Não é possível excluir uma vaga vinculada ao histórico de movimentações."
        ) from erro


def _tipo_compativel_com_movimentacao(tipo_vaga, movimentacao, caminho):
    veiculo = veiculos.buscar_por_id(movimentacao[1], caminho)
    tipo_veiculo = veiculo[4]
    pcd = movimentacao[7]
    if tipo_veiculo == 2:
        return tipo_vaga == 2
    if pcd == 1:
        return tipo_vaga in (1, 3)
    return tipo_vaga == 1
