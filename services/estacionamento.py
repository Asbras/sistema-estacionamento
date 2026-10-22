"""Regras de entrada, alocação de vagas, saída e cobrança."""

import math
from datetime import datetime

from database.connection import DEFAULT_DATABASE_PATH, conectar
from database.repositories import movimentacoes, vagas, veiculos
from database.repositories._common import validar_categoria, validar_texto_obrigatorio


TARIFA_POR_HORA = 10.0


class ErroEstacionamento(ValueError):
    """Erro de regra de negócio do estacionamento."""


def calcular_cobranca(entrada, saida):
    """Calcula R$ 10 por hora iniciada, cobrando no mínimo uma hora."""
    entrada = _como_datetime(entrada, "entrada")
    saida = _como_datetime(saida, "saída")
    segundos = (saida - entrada).total_seconds()
    horas_cobradas = max(1, math.ceil(segundos / 3600))
    return round(horas_cobradas * TARIFA_POR_HORA, 2)


def registrar_entrada(placa, usuario_entrada_id, modelo=None, cor=None, tipo=None,
                      pcd=0, momento=None, caminho=DEFAULT_DATABASE_PATH):
    """Reutiliza ou cadastra o veículo, escolhe vaga e cria a movimentação."""
    validar_texto_obrigatorio("placa", placa)
    validar_categoria("pcd", pcd, (0, 1))
    instante = _como_datetime(momento or datetime.now(), "entrada")

    conexao = conectar(caminho)
    try:
        # Serializa escritores para que a verificação e a alocação sejam atômicas.
        conexao.execute("BEGIN IMMEDIATE")
        veiculo = veiculos.buscar_por_placa(placa, conexao=conexao)
        if veiculo is None:
            if modelo is None or cor is None or tipo is None:
                raise ErroEstacionamento(
                    "Para cadastrar um veículo novo, informe modelo, cor e tipo."
                )
            validar_categoria("tipo", tipo, (1, 2))
            veiculo_id = veiculos.criar(
                placa, modelo, cor, tipo, conexao=conexao
            )
            tipo_veiculo = tipo
        else:
            veiculo_id = veiculo[0]
            tipo_veiculo = veiculo[4]

        if movimentacoes.buscar_aberta_para_veiculo(
            veiculo_id, conexao=conexao
        ) is not None:
            raise ErroEstacionamento(
                "O veículo já possui uma movimentação aberta."
            )

        if tipo_veiculo == 2 and pcd == 1:
            raise ErroEstacionamento("Atendimento PCD é permitido somente para carros.")

        tipos_de_vaga = (2,) if tipo_veiculo == 2 else ((3, 1) if pcd == 1 else (1,))
        vaga_escolhida = None
        for tipo_vaga in tipos_de_vaga:
            livres = vagas.buscar_livres_por_tipo(tipo_vaga, conexao=conexao)
            if livres:
                vaga_escolhida = livres[0]
                break
        if vaga_escolhida is None:
            categoria = "moto" if tipo_veiculo == 2 else ("carro PCD" if pcd else "carro")
            raise ErroEstacionamento(f"Não há vaga disponível para {categoria}.")

        movimentacao_id = movimentacoes.criar(
            veiculo_id,
            vaga_escolhida[0],
            usuario_entrada_id,
            instante.isoformat(),
            pcd,
            conexao=conexao,
        )
        conexao.commit()
        return movimentacao_id
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def registrar_saida(movimentacao_id, usuario_saida_id, momento=None,
                    caminho=DEFAULT_DATABASE_PATH):
    """Encerra uma movimentação aberta e registra seu valor de permanência."""
    instante = _como_datetime(momento or datetime.now(), "saída")
    conexao = conectar(caminho)
    try:
        conexao.execute("BEGIN IMMEDIATE")
        movimentacao = movimentacoes.buscar_por_id(
            movimentacao_id, conexao=conexao
        )
        if movimentacao is None or movimentacao[6] is not None:
            raise ErroEstacionamento("Não existe movimentação aberta com esse identificador.")

        entrada = _como_datetime(movimentacao[5], "entrada")
        if instante <= entrada:
            raise ErroEstacionamento(
                "O horário de saída deve ser posterior ao horário de entrada."
            )
        valor = calcular_cobranca(entrada, instante)
        atualizadas = movimentacoes.encerrar(
            movimentacao_id,
            usuario_saida_id,
            instante.isoformat(),
            valor,
            conexao=conexao,
        )
        if atualizadas != 1:
            raise ErroEstacionamento("A movimentação não pôde ser encerrada.")
        conexao.commit()
        return valor
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def obter_resumo_entrada(movimentacao_id, caminho=DEFAULT_DATABASE_PATH):
    """Retorna dados da movimentação necessários para confirmar a entrada na UI."""
    movimentacao = movimentacoes.buscar_por_id(movimentacao_id, caminho)
    if movimentacao is None:
        raise ErroEstacionamento("Movimentação não encontrada.")
    veiculo = veiculos.buscar_por_id(movimentacao[1], caminho)
    vaga = vagas.buscar_por_id(movimentacao[2], caminho)
    return {
        "id": movimentacao[0],
        "placa": veiculo[1],
        "vaga_numero": vaga[1],
        "entrada": movimentacao[5],
    }


def buscar_movimentacao_aberta_por_placa(placa, caminho=DEFAULT_DATABASE_PATH):
    """Localiza a movimentação aberta de um veículo pela placa."""
    validar_texto_obrigatorio("placa", placa)
    veiculo = veiculos.buscar_por_placa(placa, caminho)
    if veiculo is None:
        raise ErroEstacionamento("Veículo não encontrado.")
    movimentacao = movimentacoes.buscar_aberta_para_veiculo(veiculo[0], caminho)
    if movimentacao is None:
        raise ErroEstacionamento("O veículo não possui movimentação aberta.")
    return _resumo_movimentacao(movimentacao, caminho)


def listar_movimentacoes_abertas(caminho=DEFAULT_DATABASE_PATH, filtro_placa=""):
    """Retorna os dados das movimentações abertas para exibição na aplicação.

    O filtro é opcional, parcial e não diferencia maiúsculas de minúsculas.
    A consulta permanece no repository; este serviço apenas prepara os dados
    necessários para os consumidores da aplicação.
    """
    filtro_normalizado = (filtro_placa or "").strip().casefold()
    resumos = []

    for movimentacao in movimentacoes.listar_abertas(caminho):
        resumo = _resumo_movimentacao(movimentacao, caminho)
        if filtro_normalizado in resumo["placa"].casefold():
            resumos.append(resumo)

    return resumos


def obter_resumo_saida(movimentacao_id, caminho=DEFAULT_DATABASE_PATH):
    """Retorna os dados de uma movimentação encerrada para confirmação na UI."""
    movimentacao = movimentacoes.buscar_por_id(movimentacao_id, caminho)
    if movimentacao is None or movimentacao[6] is None:
        raise ErroEstacionamento("Movimentação encerrada não encontrada.")
    return _resumo_movimentacao(movimentacao, caminho)


def _resumo_movimentacao(movimentacao, caminho):
    veiculo = veiculos.buscar_por_id(movimentacao[1], caminho)
    vaga = vagas.buscar_por_id(movimentacao[2], caminho)
    return {
        "id": movimentacao[0],
        "placa": veiculo[1],
        "modelo": veiculo[2],
        "vaga_numero": vaga[1],
        "entrada": movimentacao[5],
        "saida": movimentacao[6],
        "valor": movimentacao[8],
    }


def _como_datetime(valor, campo):
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor)
        except ValueError as erro:
            raise ValueError(f"Formato inválido para {campo}; use ISO 8601.") from erro
    raise ValueError(f"{campo} deve ser um datetime ou texto ISO 8601.")
