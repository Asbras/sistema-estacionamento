"""Testes isolados dos repositórios SQLite."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from database.connection import conectar
from database.init_db import inicializar_banco
from database.repositories import movimentacoes, usuarios, vagas, veiculos


class RepositoriesTest(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self._tempdir.name) / "teste.db"
        inicializar_banco(self.database_path)

    def tearDown(self):
        self._tempdir.cleanup()

    def test_usuario_criar_buscar_atualizar_e_inativar(self):
        usuario_id = usuarios.criar("ana", "senha", self.database_path)
        self.assertEqual(usuarios.buscar_por_id(usuario_id, self.database_path)[1], "ana")
        self.assertEqual(usuarios.buscar_por_username("ana", self.database_path)[3], 1)
        self.assertEqual(len(usuarios.listar(self.database_path)), 1)
        with self.assertRaises(sqlite3.IntegrityError):
            usuarios.criar("ana", "outra", self.database_path)
        self.assertEqual(
            usuarios.atualizar(usuario_id, username="ana.s", senha="nova", caminho=self.database_path),
            1,
        )
        self.assertEqual(usuarios.buscar_por_id(usuario_id, self.database_path)[1:3], ("ana.s", "nova"))
        self.assertEqual(usuarios.definir_ativo(usuario_id, 0, self.database_path), 1)
        self.assertEqual(usuarios.definir_ativo(usuario_id, 1, self.database_path), 1)
        with self.assertRaises(ValueError):
            usuarios.definir_ativo(usuario_id, 2, self.database_path)

    def test_veiculo_criar_buscar_atualizar_e_excluir(self):
        veiculo_id = veiculos.criar("ABC1234", "Sedan", "azul", 1, self.database_path)
        self.assertEqual(veiculos.buscar_por_id(veiculo_id, self.database_path)[1], "ABC1234")
        self.assertEqual(veiculos.buscar_por_placa("ABC1234", self.database_path)[4], 1)
        self.assertEqual(len(veiculos.listar(self.database_path)), 1)
        with self.assertRaises(sqlite3.IntegrityError):
            veiculos.criar("ABC1234", "Outro", "preto", 1, self.database_path)
        self.assertEqual(
            veiculos.atualizar(veiculo_id, modelo="Hatch", tipo=2, caminho=self.database_path),
            1,
        )
        self.assertEqual(veiculos.buscar_por_id(veiculo_id, self.database_path)[2:5], ("Hatch", "azul", 2))
        self.assertEqual(veiculos.excluir(veiculo_id, self.database_path), 1)
        self.assertIsNone(veiculos.buscar_por_id(veiculo_id, self.database_path))

    def test_vaga_criar_buscar_atualizar_e_excluir(self):
        vaga_id = vagas.criar("A1", 1, self.database_path)
        self.assertEqual(vagas.buscar_por_id(vaga_id, self.database_path)[1], "A1")
        self.assertEqual(vagas.buscar_por_numero("A1", self.database_path)[2], 1)
        self.assertEqual(len(vagas.listar(self.database_path)), 1)
        with self.assertRaises(sqlite3.IntegrityError):
            vagas.criar("A1", 2, self.database_path)
        self.assertEqual(vagas.atualizar(vaga_id, numero="A2", tipo=3, caminho=self.database_path), 1)
        self.assertEqual(vagas.buscar_por_id(vaga_id, self.database_path)[1:], ("A2", 3))
        self.assertEqual(vagas.excluir(vaga_id, self.database_path), 1)
        self.assertIsNone(vagas.buscar_por_id(vaga_id, self.database_path))

    def test_consultas_movimentacao_aberta_e_historico(self):
        usuario_id = usuarios.criar("funcionario", "senha", self.database_path)
        veiculo_id = veiculos.criar("XYZ9876", "Moto", "vermelha", 2, self.database_path)
        vaga_id = vagas.criar("M1", 2, self.database_path)
        conexao = conectar(self.database_path)
        try:
            cursor = conexao.execute(
                "INSERT INTO movimentacao "
                "(veiculo_id, vaga_id, usuario_entrada_id, entrada, pcd) "
                "VALUES (?, ?, ?, ?, ?)",
                (veiculo_id, vaga_id, usuario_id, "2026-01-01T10:00:00", 0),
            )
            aberta_id = cursor.lastrowid
            cursor = conexao.execute(
                "INSERT INTO movimentacao "
                "(veiculo_id, vaga_id, usuario_entrada_id, entrada, saida, pcd, valor) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (veiculo_id, vaga_id, usuario_id, "2025-12-01T10:00:00", "2025-12-01T11:00:00", 0, 10.0),
            )
            fechada_id = cursor.lastrowid
            conexao.commit()
        finally:
            conexao.close()

        self.assertEqual(movimentacoes.buscar_por_id(aberta_id, self.database_path)[0], aberta_id)
        self.assertEqual(len(movimentacoes.listar(self.database_path)), 2)
        self.assertEqual([linha[0] for linha in movimentacoes.listar_abertas(self.database_path)], [aberta_id])
        self.assertTrue(movimentacoes.existe_aberta_para_veiculo(veiculo_id, self.database_path))
        self.assertTrue(movimentacoes.existe_aberta_para_vaga(vaga_id, self.database_path))
        self.assertIsNotNone(movimentacoes.buscar_por_id(fechada_id, self.database_path))

    def test_exclusao_referenciada_e_restrita(self):
        usuario_id = usuarios.criar("referenciado", "senha", self.database_path)
        veiculo_id = veiculos.criar("REF1234", "Carro", "branco", 1, self.database_path)
        vaga_id = vagas.criar("R1", 1, self.database_path)
        conexao = conectar(self.database_path)
        try:
            conexao.execute(
                "INSERT INTO movimentacao "
                "(veiculo_id, vaga_id, usuario_entrada_id, entrada, pcd) "
                "VALUES (?, ?, ?, ?, 0)",
                (veiculo_id, vaga_id, usuario_id, "2026-01-01T10:00:00"),
            )
            conexao.commit()
        finally:
            conexao.close()
        with self.assertRaises(sqlite3.IntegrityError):
            veiculos.excluir(veiculo_id, self.database_path)
        with self.assertRaises(sqlite3.IntegrityError):
            vagas.excluir(vaga_id, self.database_path)
        self.assertEqual(usuarios.definir_ativo(usuario_id, 0, self.database_path), 1)
        conexao = conectar(self.database_path)
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                conexao.execute("DELETE FROM usuario WHERE id = ?", (usuario_id,))
            conexao.rollback()
        finally:
            conexao.close()


if __name__ == "__main__":
    unittest.main()
