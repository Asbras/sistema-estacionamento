"""Testes isolados de hash de senha e autenticação."""

import tempfile
import unittest
from pathlib import Path

from database.init_db import inicializar_banco
from database.passwords import gerar_hash_senha, verificar_senha
from database.repositories import usuarios
from services.autenticacao import ErroAutenticacao, autenticar


class AutenticacaoTest(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self._tempdir.name) / "autenticacao.db"
        inicializar_banco(self.database_path)

    def tearDown(self):
        self._tempdir.cleanup()

    def test_usuario_criado_nao_armazena_senha_em_texto_puro(self):
        usuario_id = usuarios.criar("ana", "segredo", self.database_path)
        armazenada = usuarios.buscar_por_id(usuario_id, self.database_path)[2]
        self.assertNotEqual(armazenada, "segredo")
        self.assertTrue(verificar_senha("segredo", armazenada))

    def test_senhas_iguais_recebem_hashes_diferentes_por_causa_do_salt(self):
        primeiro = gerar_hash_senha("mesma senha")
        segundo = gerar_hash_senha("mesma senha")
        self.assertNotEqual(primeiro, segundo)
        self.assertTrue(verificar_senha("mesma senha", primeiro))
        self.assertTrue(verificar_senha("mesma senha", segundo))

    def test_verificacao_rejeita_senha_incorreta(self):
        armazenada = gerar_hash_senha("correta")
        self.assertFalse(verificar_senha("incorreta", armazenada))

    def test_usuario_ativo_autentica_e_nao_expoe_hash(self):
        usuario_id = usuarios.criar("ativo", "segredo", self.database_path)
        dados = autenticar("ativo", "segredo", self.database_path)
        self.assertEqual(dados, {"id": usuario_id, "username": "ativo", "ativo": 1})

    def test_usuario_inexistente_e_rejeitado_com_erro_generico(self):
        with self.assertRaisesRegex(ErroAutenticacao, "Usuário ou senha inválidos"):
            autenticar("desconhecido", "qualquer", self.database_path)

    def test_senha_incorreta_e_rejeitada_com_erro_generico(self):
        usuarios.criar("ana", "correta", self.database_path)
        with self.assertRaisesRegex(ErroAutenticacao, "Usuário ou senha inválidos"):
            autenticar("ana", "incorreta", self.database_path)

    def test_usuario_inativo_nao_autentica(self):
        usuario_id = usuarios.criar("inativo", "segredo", self.database_path)
        usuarios.definir_ativo(usuario_id, 0, self.database_path)
        with self.assertRaisesRegex(ErroAutenticacao, "Usuário inativo"):
            autenticar("inativo", "segredo", self.database_path)

    def test_alteracao_de_senha_invalida_anterior_e_aceita_nova(self):
        usuario_id = usuarios.criar("ana", "anterior", self.database_path)
        usuarios.atualizar(usuario_id, senha="nova", caminho=self.database_path)
        armazenada = usuarios.buscar_por_id(usuario_id, self.database_path)[2]
        self.assertNotEqual(armazenada, "nova")
        self.assertFalse(verificar_senha("anterior", armazenada))
        self.assertTrue(verificar_senha("nova", armazenada))
        with self.assertRaisesRegex(ErroAutenticacao, "Usuário ou senha inválidos"):
            autenticar("ana", "anterior", self.database_path)
        self.assertEqual(autenticar("ana", "nova", self.database_path)["id"], usuario_id)


if __name__ == "__main__":
    unittest.main()
