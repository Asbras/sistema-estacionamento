"""Testes isolados da importação de marcas FIPE pela BrasilAPI."""

import io
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request

from database.init_db import inicializar_banco
from database.repositories import marcas_importadas
from services.importacao import (
    ErroImportacao,
    importar_marcas,
    limpar_marcas_importadas,
    listar_marcas_importadas,
)


class RespostaFalsa:
    def __init__(self, dados):
        self.conteudo = json.dumps(dados).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, tipo, valor, traceback):
        return False

    def read(self):
        return self.conteudo


class ImportacaoTest(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self._tempdir.name) / "importacao.db"
        inicializar_banco(self.database_path)
        self.momento = datetime(2026, 10, 22, 10, 0)

    def tearDown(self):
        self._tempdir.cleanup()

    def _abrir_com(self, dados):
        def abrir(requisicao, timeout):
            self.assertEqual(timeout, 10)
            self.assertIsInstance(requisicao, Request)
            self.assertEqual(
                requisicao.get_header("User-agent"),
                "SistemaEstacionamento-FATEC/1.0",
            )
            self.assertEqual(requisicao.get_header("Accept"), "application/json")
            return RespostaFalsa(dados)
        return abrir

    def test_importa_marcas_de_carros_e_motos_e_armazena_no_banco(self):
        carros = [{"nome": "FIAT", "valor": "21"}, {"nome": "Ford", "valor": "22"}]
        motos = [{"nome": "Honda", "valor": "1"}]
        resultado_carros = importar_marcas(
            "carros",
            self.database_path,
            abrir_url=self._abrir_com(carros),
            momento=self.momento,
        )
        resultado_motos = importar_marcas(
            "motos",
            self.database_path,
            abrir_url=self._abrir_com(motos),
            momento=self.momento,
        )

        self.assertEqual(resultado_carros, {"tipo": "CARRO", "recebidos": 2, "salvos": 2})
        self.assertEqual(resultado_motos, {"tipo": "MOTO", "recebidos": 1, "salvos": 1})
        marcas = listar_marcas_importadas(self.database_path)
        self.assertEqual([marca["tipo_nome"] for marca in marcas], ["CARRO", "CARRO", "MOTO"])
        self.assertEqual(marcas[0]["importado_em"], self.momento.isoformat())

    def test_duplicacao_e_filtros_por_tipo_e_nome(self):
        carros = [{"nome": "FIAT", "valor": "21"}, {"nome": "Ford", "valor": "22"}]
        importar_marcas("carros", self.database_path, abrir_url=self._abrir_com(carros))
        repetida = importar_marcas("carros", self.database_path, abrir_url=self._abrir_com(carros))
        self.assertEqual(repetida["salvos"], 0)

        por_tipo = listar_marcas_importadas(self.database_path, tipo=1)
        self.assertEqual(len(por_tipo), 2)
        por_nome = listar_marcas_importadas(self.database_path, filtro_nome="ia")
        self.assertEqual([marca["nome"] for marca in por_nome], ["FIAT"])

    def test_limpeza_remove_somente_marcas_importadas(self):
        importar_marcas(
            "motos",
            self.database_path,
            abrir_url=self._abrir_com([{"nome": "Honda", "valor": "1"}]),
        )
        self.assertEqual(limpar_marcas_importadas(self.database_path), 1)
        self.assertEqual(listar_marcas_importadas(self.database_path), [])

    def test_erro_de_rede_ou_resposta_invalida_nao_remove_dados_existentes(self):
        importar_marcas(
            "carros",
            self.database_path,
            abrir_url=self._abrir_com([{"nome": "FIAT", "valor": "21"}]),
        )

        def falha_rede(_requisicao, timeout):
            raise URLError("sem conexão")

        def falha_http(_requisicao, timeout):
            erro = HTTPError(
                "https://brasilapi.com.br", 403, "Forbidden", None, io.BytesIO()
            )
            try:
                raise erro
            finally:
                erro.close()

        with self.assertRaisesRegex(ErroImportacao, "conectar"):
            importar_marcas("motos", self.database_path, abrir_url=falha_rede)
        with self.assertRaisesRegex(ErroImportacao, "HTTP 403"):
            importar_marcas(
                "motos",
                self.database_path,
                abrir_url=falha_http,
            )
        with self.assertRaisesRegex(ErroImportacao, "resposta inválida"):
            importar_marcas(
                "motos",
                self.database_path,
                abrir_url=self._abrir_com({"nome": "Honda", "valor": "1"}),
            )

        marcas = listar_marcas_importadas(self.database_path)
        self.assertEqual([(marca["tipo"], marca["codigo"]) for marca in marcas], [(1, "21")])

    def test_repository_expoe_insert_select_e_delete(self):
        marca_id = marcas_importadas.salvar(
            1, "21", "FIAT", self.momento.isoformat(), self.database_path
        )
        self.assertEqual(marca_id, 1)
        self.assertEqual(marcas_importadas.listar(caminho=self.database_path)[0][3], "FIAT")
        self.assertEqual(marcas_importadas.limpar(self.database_path), 1)


if __name__ == "__main__":
    unittest.main()
