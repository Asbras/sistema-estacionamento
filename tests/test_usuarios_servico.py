"""Testes das regras de gerenciamento de usuários."""

import tempfile
import unittest
from pathlib import Path

from database.init_db import inicializar_banco
from database.passwords import verificar_senha
from database.repositories import usuarios
from services.autenticacao import ErroAutenticacao, autenticar
from services.usuarios import (
    ErroUsuario,
    atualizar_usuario,
    cadastrar_usuario,
    definir_situacao_usuario,
    listar_usuarios,
)


class UsuariosServicoTest(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self._tempdir.name) / "usuarios.db"
        inicializar_banco(self.database_path)

    def tearDown(self):
        self._tempdir.cleanup()

    def test_cadastro_armazena_hash_rejeita_duplicidade_e_filtra_username(self):
        usuario_id = cadastrar_usuario("Ana", "segredo", "segredo", self.database_path)
        cadastrar_usuario("Bruno", "senha", "senha", self.database_path)
        armazenada = usuarios.buscar_por_id(usuario_id, self.database_path)[2]
        self.assertNotEqual(armazenada, "segredo")
        self.assertTrue(verificar_senha("segredo", armazenada))

        with self.assertRaisesRegex(ErroUsuario, "Já existe"):
            cadastrar_usuario("Ana", "outra", "outra", self.database_path)

        filtrados = listar_usuarios(self.database_path, "an")
        self.assertEqual(filtrados, [{
            "id": usuario_id,
            "username": "Ana",
            "ativo": 1,
            "situacao": "ATIVO",
        }])

    def test_atualizacao_de_username_e_senha_invalida_senha_anterior(self):
        usuario_id = cadastrar_usuario("ana", "anterior", "anterior", self.database_path)
        atualizar_usuario(
            usuario_id,
            "ana.nova",
            "nova",
            "nova",
            self.database_path,
        )
        self.assertEqual(usuarios.buscar_por_id(usuario_id, self.database_path)[1], "ana.nova")
        with self.assertRaisesRegex(ErroAutenticacao, "Usuário ou senha inválidos"):
            autenticar("ana", "anterior", self.database_path)
        self.assertEqual(
            autenticar("ana.nova", "nova", self.database_path)["id"], usuario_id
        )

    def test_ativacao_desativacao_e_protecao_da_conta_autenticada(self):
        usuario_atual_id = cadastrar_usuario(
            "atual", "senha", "senha", self.database_path
        )
        outro_id = cadastrar_usuario("outro", "senha", "senha", self.database_path)

        definir_situacao_usuario(outro_id, 0, usuario_atual_id, self.database_path)
        self.assertEqual(listar_usuarios(self.database_path, "outro")[0]["situacao"], "INATIVO")
        with self.assertRaisesRegex(ErroAutenticacao, "Usuário inativo"):
            autenticar("outro", "senha", self.database_path)

        definir_situacao_usuario(outro_id, 1, usuario_atual_id, self.database_path)
        self.assertEqual(autenticar("outro", "senha", self.database_path)["id"], outro_id)
        with self.assertRaisesRegex(ErroUsuario, "autenticado"):
            definir_situacao_usuario(usuario_atual_id, 0, usuario_atual_id, self.database_path)
        self.assertEqual(listar_usuarios(self.database_path, "atual")[0]["situacao"], "ATIVO")


if __name__ == "__main__":
    unittest.main()
