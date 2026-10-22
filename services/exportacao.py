"""Exportação somente de leitura dos dados do sistema."""

import json
import zipfile
from datetime import datetime
from pathlib import Path

from database.connection import DEFAULT_DATABASE_PATH, PROJECT_ROOT
from database.repositories import (
    marcas_importadas,
    movimentacoes,
    usuarios,
    vagas,
    veiculos,
)


DEFAULT_EXPORTS_PATH = PROJECT_ROOT / "exports"


class ErroExportacao(ValueError):
    """Erro ao gerar os arquivos de exportação."""


def exportar_dados(caminho_banco=DEFAULT_DATABASE_PATH,
                   diretorio_saida=DEFAULT_EXPORTS_PATH, momento=None):
    """Gera um JSON legível e um ZIP contendo esse JSON."""
    instante = momento or datetime.now()
    dados = _montar_dados(caminho_banco, instante)

    try:
        diretorio = Path(diretorio_saida)
        diretorio.mkdir(parents=True, exist_ok=True)
        caminho_json, caminho_zip = _caminhos_disponiveis(diretorio, instante)
        caminho_json.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as arquivo_zip:
            arquivo_zip.write(caminho_json, arcname=caminho_json.name)
    except (OSError, TypeError, ValueError, zipfile.BadZipFile) as erro:
        raise ErroExportacao("Não foi possível gerar os arquivos de exportação.") from erro

    return {
        "json": caminho_json,
        "zip": caminho_zip,
        "exportado_em": instante.isoformat(),
    }


def _montar_dados(caminho_banco, instante):
    return {
        "formato_versao": 1,
        "exportado_em": instante.isoformat(),
        "usuario": [
            {"id": usuario[0], "username": usuario[1], "ativo": usuario[3]}
            for usuario in usuarios.listar(caminho_banco)
        ],
        "veiculo": [
            {
                "id": veiculo[0],
                "placa": veiculo[1],
                "modelo": veiculo[2],
                "cor": veiculo[3],
                "tipo": veiculo[4],
            }
            for veiculo in veiculos.listar(caminho_banco)
        ],
        "vaga": [
            {"id": vaga[0], "numero": vaga[1], "tipo": vaga[2]}
            for vaga in vagas.listar(caminho_banco)
        ],
        "movimentacao": [
            {
                "id": movimentacao[0],
                "veiculo_id": movimentacao[1],
                "vaga_id": movimentacao[2],
                "usuario_entrada_id": movimentacao[3],
                "usuario_saida_id": movimentacao[4],
                "entrada": movimentacao[5],
                "saida": movimentacao[6],
                "pcd": movimentacao[7],
                "valor": movimentacao[8],
            }
            for movimentacao in movimentacoes.listar(caminho_banco)
        ],
        "marca_importada": [
            {
                "id": marca[0],
                "tipo": marca[1],
                "codigo": marca[2],
                "nome": marca[3],
                "importado_em": marca[4],
            }
            for marca in marcas_importadas.listar(caminho=caminho_banco)
        ],
    }


def _caminhos_disponiveis(diretorio, instante):
    nome_base = f"estacionamento_{instante.strftime('%Y-%m-%d_%H%M%S')}"
    indice = 0
    while True:
        sufixo = "" if indice == 0 else f"_{indice}"
        caminho_json = diretorio / f"{nome_base}{sufixo}.json"
        caminho_zip = diretorio / f"{nome_base}{sufixo}.zip"
        if not caminho_json.exists() and not caminho_zip.exists():
            return caminho_json, caminho_zip
        indice += 1
