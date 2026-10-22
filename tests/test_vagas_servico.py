"""Testes das regras de gerenciamento de vagas."""

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from database.init_db import inicializar_banco
from database.repositories import usuarios
from services.estacionamento import registrar_entrada, registrar_saida
from services.vagas import (
    ErroVaga,
    atualizar_vaga,
    cadastrar_vaga,
    excluir_vaga,
    listar_vagas,
)


class VagasServicoTest(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self._tempdir.name) / "vagas.db"
        inicializar_banco(self.database_path)
        self.usuario_id = usuarios.criar("funcionario", "senha", self.database_path)
        self.agora = datetime(2026, 10, 22, 10, 0)

    def tearDown(self):
        self._tempdir.cleanup()

    def test_listagem_mostra_situacao_livre_e_ocupada(self):
        carro_id = cadastrar_vaga("C1", 1, self.database_path)
        cadastrar_vaga("M1", 2, self.database_path)
        registrar_entrada(
            "CARRO1", self.usuario_id, "Modelo", "Cor", 1,
            momento=self.agora, caminho=self.database_path,
        )

        vagas = listar_vagas(self.database_path)
        por_id = {vaga["id"]: vaga for vaga in vagas}
        self.assertEqual(por_id[carro_id]["tipo_nome"], "CARRO")
        self.assertEqual(por_id[carro_id]["situacao"], "OCUPADA")
        self.assertEqual(por_id[carro_id + 1]["situacao"], "LIVRE")

    def test_alteracao_incompativel_em_vaga_ocupada_e_rejeitada(self):
        vaga_id = cadastrar_vaga("C1", 1, self.database_path)
        registrar_entrada(
            "CARRO1", self.usuario_id, "Modelo", "Cor", 1,
            momento=self.agora, caminho=self.database_path,
        )

        with self.assertRaisesRegex(ErroVaga, "incompatível"):
            atualizar_vaga(vaga_id, "C1", 3, self.database_path)
        self.assertEqual(
            next(vaga for vaga in listar_vagas(self.database_path) if vaga["id"] == vaga_id)["tipo"],
            1,
        )

    def test_exclusao_de_vaga_livre_e_de_vaga_com_historico(self):
        livre_id = cadastrar_vaga("L1", 1, self.database_path)
        self.assertEqual(excluir_vaga(livre_id, self.database_path), 1)

        historico_id = cadastrar_vaga("H1", 1, self.database_path)
        movimentacao_id = registrar_entrada(
            "CARRO1", self.usuario_id, "Modelo", "Cor", 1,
            momento=self.agora, caminho=self.database_path,
        )
        registrar_saida(
            movimentacao_id,
            self.usuario_id,
            self.agora + timedelta(minutes=5),
            self.database_path,
        )

        with self.assertRaisesRegex(ErroVaga, "histórico"):
            excluir_vaga(historico_id, self.database_path)


if __name__ == "__main__":
    unittest.main()
