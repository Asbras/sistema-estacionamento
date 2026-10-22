"""Importação de marcas FIPE publicadas pela BrasilAPI."""

import json
from datetime import datetime
from urllib import error, request

from database.connection import DEFAULT_DATABASE_PATH, conectar
from database.repositories import marcas_importadas


URL_MARCAS = "https://brasilapi.com.br/api/fipe/marcas/v1/{}"
HEADERS_BRASIL_API = {
    "User-Agent": "SistemaEstacionamento-FATEC/1.0",
    "Accept": "application/json",
}
TIPOS_WEB = {"carros": 1, "motos": 2}
TIPOS_NOME = {1: "CARRO", 2: "MOTO"}
TIMEOUT_PADRAO = 10


class ErroImportacao(ValueError):
    """Erro de consulta ou validação durante a importação de marcas."""


def importar_marcas(tipo_web, caminho=DEFAULT_DATABASE_PATH, abrir_url=None,
                    timeout=TIMEOUT_PADRAO, momento=None):
    """Obtém e armazena marcas de carros ou motos sem apagar dados existentes."""
    tipo = _obter_tipo(tipo_web)
    marcas = consultar_marcas(tipo_web, abrir_url=abrir_url, timeout=timeout)
    importado_em = (momento or datetime.now()).isoformat()

    conexao = conectar(caminho)
    try:
        salvos = 0
        for marca in marcas:
            salvos += marcas_importadas.salvar(
                tipo,
                marca["valor"],
                marca["nome"],
                importado_em,
                conexao=conexao,
            )
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()

    return {
        "tipo": TIPOS_NOME[tipo],
        "recebidos": len(marcas),
        "salvos": salvos,
    }


def importar_carros_e_motos(caminho=DEFAULT_DATABASE_PATH, abrir_url=None,
                            timeout=TIMEOUT_PADRAO, momento=None):
    """Importa marcas de carros e motos, em consultas independentes."""
    return [
        importar_marcas(
            tipo_web,
            caminho=caminho,
            abrir_url=abrir_url,
            timeout=timeout,
            momento=momento,
        )
        for tipo_web in TIPOS_WEB
    ]


def consultar_marcas(tipo_web, abrir_url=None, timeout=TIMEOUT_PADRAO):
    """Consulta e valida a lista de marcas documentada pela BrasilAPI/FIPE."""
    _obter_tipo(tipo_web)
    abrir = abrir_url or request.urlopen
    url = URL_MARCAS.format(tipo_web)
    requisicao = request.Request(url, headers=HEADERS_BRASIL_API)
    try:
        with abrir(requisicao, timeout=timeout) as resposta:
            conteudo = resposta.read()
    except error.HTTPError as erro:
        raise ErroImportacao(
            f"A BrasilAPI não pôde atender à solicitação (HTTP {erro.code})."
        ) from erro
    except (error.URLError, TimeoutError, OSError) as erro:
        raise ErroImportacao(
            "Não foi possível conectar à BrasilAPI. Tente novamente mais tarde."
        ) from erro

    try:
        dados = json.loads(conteudo.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as erro:
        raise ErroImportacao("A BrasilAPI retornou uma resposta inválida.") from erro
    return _validar_marcas(dados)


def listar_marcas_importadas(caminho=DEFAULT_DATABASE_PATH, tipo=None, filtro_nome=""):
    """Lista as marcas armazenadas com filtro opcional por tipo e nome."""
    if tipo is not None and tipo not in TIPOS_NOME:
        raise ValueError("tipo deve ser CARRO, MOTO ou TODOS.")
    filtro_normalizado = (filtro_nome or "").strip().casefold()
    resultado = []
    for marca in marcas_importadas.listar(tipo=tipo, caminho=caminho):
        if filtro_normalizado not in marca[3].casefold():
            continue
        resultado.append(
            {
                "id": marca[0],
                "tipo": marca[1],
                "tipo_nome": TIPOS_NOME[marca[1]],
                "codigo": marca[2],
                "nome": marca[3],
                "importado_em": marca[4],
            }
        )
    return resultado


def limpar_marcas_importadas(caminho=DEFAULT_DATABASE_PATH):
    """Limpa somente a tabela de marcas importadas."""
    return marcas_importadas.limpar(caminho)


def _obter_tipo(tipo_web):
    try:
        return TIPOS_WEB[tipo_web]
    except KeyError as erro:
        raise ValueError("tipo de veículo deve ser carros ou motos.") from erro


def _validar_marcas(dados):
    if not isinstance(dados, list):
        raise ErroImportacao("A BrasilAPI retornou uma resposta inválida.")

    marcas = []
    for marca in dados:
        if not isinstance(marca, dict):
            raise ErroImportacao("A BrasilAPI retornou uma resposta inválida.")
        nome = marca.get("nome")
        valor = marca.get("valor")
        if not isinstance(nome, str) or not nome.strip():
            raise ErroImportacao("A BrasilAPI retornou uma resposta inválida.")
        if not isinstance(valor, str) or not valor.strip():
            raise ErroImportacao("A BrasilAPI retornou uma resposta inválida.")
        marcas.append({"nome": nome.strip(), "valor": valor.strip()})
    return marcas
