"""Testes das regras de gerenciamento de veículos."""

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from database.init_db import inicializar_banco
from database.repositories import usuarios, vagas
from services.estacionamento import registrar_entrada, registrar_saida
from services.veiculos import (
    ErroVeiculo,
    atualizar_veiculo,
    cadastrar_veiculo,
    excluir_veiculo,
    listar_veiculos,
)


class VeiculosServicoTest(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self._tempdir.name) / "veiculos.db"
        inicializar_banco(self.database_path)
        self.usuario_id = usuarios.criar("funcionario", "senha", self.database_path)
        self.agora = datetime(2026, 10, 22, 10, 0)

    def tearDown(self):
        self._tempdir.cleanup()

    def test_cadastro_atualizacao_e_filtro_por_placa(self):
        veiculo_id = cadastrar_veiculo(
            "ABC1234", "Sedan", "Azul", 1, self.database_path
        )
        cadastrar_veiculo("XYZ9876", "Moto", "Preta", 2, self.database_path)

        filtrados = listar_veiculos(self.database_path, "bc1")
        self.assertEqual(len(filtrados), 1)
        self.assertEqual(filtrados[0]["id"], veiculo_id)
        self.assertEqual(filtrados[0]["tipo_nome"], "CARRO")

        atualizar_veiculo(
            veiculo_id, "ABC1234", "Hatch", "Vermelha", 1, self.database_path
        )
        atualizado = listar_veiculos(self.database_path, "abc")
        self.assertEqual(atualizado[0]["modelo"], "Hatch")
        self.assertEqual(atualizado[0]["cor"], "Vermelha")

    def test_alteracao_de_tipo_incompativel_com_movimentacao_aberta_e_rejeitada(self):
        veiculo_id = cadastrar_veiculo(
            "ABC1234", "Sedan", "Azul", 1, self.database_path
        )
        vagas.criar("C1", 1, self.database_path)
        registrar_entrada(
            "ABC1234",
            self.usuario_id,
            momento=self.agora,
            caminho=self.database_path,
        )

        with self.assertRaisesRegex(ErroVeiculo, "incompatível"):
            atualizar_veiculo(
                veiculo_id, "ABC1234", "Sedan", "Azul", 2, self.database_path
            )
        self.assertEqual(listar_veiculos(self.database_path)[0]["tipo"], 1)

    def test_exclusao_rejeita_movimentacao_aberta_ou_historico_e_permite_sem_vinculo(self):
        livre_id = cadastrar_veiculo("LIVRE1", "Sedan", "Azul", 1, self.database_path)
        self.assertEqual(excluir_veiculo(livre_id, self.database_path), 1)

        aberto_id = cadastrar_veiculo("ABERTO1", "Sedan", "Azul", 1, self.database_path)
        vagas.criar("C1", 1, self.database_path)
        movimentacao_id = registrar_entrada(
            "ABERTO1",
            self.usuario_id,
            momento=self.agora,
            caminho=self.database_path,
        )
        with self.assertRaisesRegex(ErroVeiculo, "estacionado"):
            excluir_veiculo(aberto_id, self.database_path)

        registrar_saida(
            movimentacao_id,
            self.usuario_id,
            self.agora + timedelta(minutes=5),
            self.database_path,
        )
        with self.assertRaisesRegex(ErroVeiculo, "histórico"):
            excluir_veiculo(aberto_id, self.database_path)


if __name__ == "__main__":
    unittest.main()
