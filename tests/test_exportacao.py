"""Testes isolados da exportação de dados para JSON e ZIP."""

import json
import tempfile
import unittest
import zipfile
from datetime import datetime
from pathlib import Path

from database.init_db import inicializar_banco
from database.repositories import (
    marcas_importadas,
    movimentacoes,
    usuarios,
    vagas,
    veiculos,
)
from services.exportacao import ErroExportacao, exportar_dados


class ExportacaoTest(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.diretorio = Path(self._tempdir.name)
        self.database_path = self.diretorio / "exportacao.db"
        self.diretorio_exportacao = self.diretorio / "arquivos"
        self.momento = datetime(2026, 10, 22, 10, 30, 15)
        inicializar_banco(self.database_path)

    def tearDown(self):
        self._tempdir.cleanup()

    def _criar_dados(self):
        usuario_id = usuarios.criar("operador", "senha-segura", self.database_path)
        veiculo_id = veiculos.criar(
            "ABC1234", "Café Turbo", "Azul", 1, self.database_path
        )
        vaga_id = vagas.criar("C1", 1, self.database_path)
        movimentacoes.criar(
            veiculo_id,
            vaga_id,
            usuario_id,
            "2026-10-22T10:00:00",
            0,
            self.database_path,
        )
        marcas_importadas.salvar(
            1, "21", "Móbile", "2026-10-22T10:00:00", self.database_path
        )

    def test_gera_json_e_zip_com_todos_os_dados_sem_senha(self):
        self._criar_dados()
        antes = {
            "usuario": usuarios.listar(self.database_path),
            "veiculo": veiculos.listar(self.database_path),
            "vaga": vagas.listar(self.database_path),
            "movimentacao": movimentacoes.listar(self.database_path),
            "marca_importada": marcas_importadas.listar(caminho=self.database_path),
        }

        resultado = exportar_dados(
            self.database_path, self.diretorio_exportacao, self.momento
        )

        self.assertTrue(resultado["json"].is_file())
        self.assertTrue(resultado["zip"].is_file())
        texto_json = resultado["json"].read_text(encoding="utf-8")
        self.assertIn("Café Turbo", texto_json)
        self.assertIn("Móbile", texto_json)
        dados = json.loads(texto_json)
        self.assertEqual(
            set(dados),
            {
                "formato_versao",
                "exportado_em",
                "usuario",
                "veiculo",
                "vaga",
                "movimentacao",
                "marca_importada",
            },
        )
        self.assertEqual(dados["usuario"], [{"id": 1, "username": "operador", "ativo": 1}])
        self.assertNotIn("senha", dados["usuario"][0])
        self.assertEqual(dados["veiculo"][0]["modelo"], "Café Turbo")
        self.assertEqual(dados["vaga"][0]["numero"], "C1")
        self.assertEqual(dados["movimentacao"][0]["entrada"], "2026-10-22T10:00:00")
        self.assertEqual(dados["marca_importada"][0]["nome"], "Móbile")

        with zipfile.ZipFile(resultado["zip"]) as arquivo_zip:
            self.assertEqual(arquivo_zip.namelist(), [resultado["json"].name])
            dados_no_zip = json.loads(
                arquivo_zip.read(resultado["json"].name).decode("utf-8")
            )
        self.assertEqual(dados_no_zip, dados)
        self.assertEqual(
            antes,
            {
                "usuario": usuarios.listar(self.database_path),
                "veiculo": veiculos.listar(self.database_path),
                "vaga": vagas.listar(self.database_path),
                "movimentacao": movimentacoes.listar(self.database_path),
                "marca_importada": marcas_importadas.listar(caminho=self.database_path),
            },
        )

    def test_tabelas_sem_registros_sao_exportadas_como_listas_vazias(self):
        resultado = exportar_dados(
            self.database_path, self.diretorio_exportacao, self.momento
        )
        dados = json.loads(resultado["json"].read_text(encoding="utf-8"))

        for tabela in ("usuario", "veiculo", "vaga", "movimentacao", "marca_importada"):
            self.assertEqual(dados[tabela], [])

    def test_exportacoes_sucessivas_nao_sobrescrevem_arquivos(self):
        primeiro = exportar_dados(
            self.database_path, self.diretorio_exportacao, self.momento
        )
        segundo = exportar_dados(
            self.database_path, self.diretorio_exportacao, self.momento
        )

        self.assertNotEqual(primeiro["json"], segundo["json"])
        self.assertNotEqual(primeiro["zip"], segundo["zip"])
        self.assertTrue(primeiro["json"].is_file())
        self.assertTrue(primeiro["zip"].is_file())
        self.assertTrue(segundo["json"].is_file())
        self.assertTrue(segundo["zip"].is_file())

    def test_erro_de_escrita_e_transformado_em_erro_claro(self):
        arquivo_no_lugar_do_diretorio = self.diretorio / "nao-e-diretorio"
        arquivo_no_lugar_do_diretorio.write_text("conteúdo", encoding="utf-8")

        with self.assertRaisesRegex(ErroExportacao, "Não foi possível gerar"):
            exportar_dados(
                self.database_path, arquivo_no_lugar_do_diretorio, self.momento
            )


if __name__ == "__main__":
    unittest.main()
