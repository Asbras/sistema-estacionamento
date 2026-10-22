"""Testes isolados das regras de entrada, saída e cobrança."""

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from database.init_db import inicializar_banco
from database.repositories import movimentacoes, usuarios, vagas, veiculos
from services.estacionamento import (
    ErroEstacionamento,
    calcular_cobranca,
    registrar_entrada,
    registrar_saida,
)


class EstacionamentoTest(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self._tempdir.name) / "estacionamento.db"
        inicializar_banco(self.database_path)
        self.usuario_id = usuarios.criar("funcionario", "senha", self.database_path)
        self.agora = datetime(2026, 10, 22, 10, 0)

    def tearDown(self):
        self._tempdir.cleanup()

    def vaga(self, numero, tipo):
        return vagas.criar(numero, tipo, self.database_path)

    def entrada(self, placa, tipo, pcd=0, **kwargs):
        momento = kwargs.pop("momento", self.agora)
        return registrar_entrada(
            placa=placa,
            usuario_entrada_id=self.usuario_id,
            modelo="Modelo",
            cor="Prata",
            tipo=tipo,
            pcd=pcd,
            momento=momento,
            caminho=self.database_path,
            **kwargs,
        )

    def movimentacao(self, movimentacao_id):
        return movimentacoes.buscar_por_id(movimentacao_id, self.database_path)

    def test_carro_comum_usa_vaga_carro_e_nunca_pcd(self):
        pcd_id = self.vaga("P1", 3)
        carro_id = self.vaga("C1", 1)
        mov_id = self.entrada("CARRO1", 1)
        self.assertEqual(self.movimentacao(mov_id)[2], carro_id)
        self.assertNotEqual(self.movimentacao(mov_id)[2], pcd_id)

    def test_moto_usa_somente_vaga_moto(self):
        self.vaga("C1", 1)
        self.vaga("P1", 3)
        moto_id = self.vaga("M1", 2)
        mov_id = self.entrada("MOTO1", 2)
        self.assertEqual(self.movimentacao(mov_id)[2], moto_id)

    def test_moto_pcd_e_rejeitada(self):
        self.vaga("M1", 2)
        with self.assertRaises(ErroEstacionamento):
            self.entrada("MOTO1", 2, pcd=1)
        self.assertEqual(movimentacoes.listar(self.database_path), [])

    def test_carro_pcd_prioriza_vaga_pcd(self):
        convencional_id = self.vaga("C1", 1)
        pcd_id = self.vaga("P1", 3)
        mov_id = self.entrada("CARRO1", 1, pcd=1)
        self.assertEqual(self.movimentacao(mov_id)[2], pcd_id)
        self.assertNotEqual(self.movimentacao(mov_id)[2], convencional_id)

    def test_carro_pcd_usa_convencional_quando_pcd_ocupada(self):
        pcd_id = self.vaga("P1", 3)
        carro_id = self.vaga("C1", 1)
        self.entrada("OCUPANTE", 1, pcd=1)
        mov_id = self.entrada("CARRO2", 1, pcd=1)
        self.assertEqual(self.movimentacao(mov_id)[2], carro_id)
        self.assertNotEqual(self.movimentacao(mov_id)[2], pcd_id)

    def test_falta_de_vaga_nao_cria_movimentacao(self):
        with self.assertRaisesRegex(ErroEstacionamento, "Não há vaga disponível"):
            self.entrada("CARRO1", 1)
        self.assertEqual(movimentacoes.listar(self.database_path), [])

    def test_veiculo_nao_pode_ter_duas_movimentacoes_abertas(self):
        self.vaga("C1", 1)
        self.vaga("C2", 1)
        self.entrada("CARRO1", 1)
        with self.assertRaisesRegex(ErroEstacionamento, "já possui"):
            self.entrada("CARRO1", 1)
        self.assertEqual(len(movimentacoes.listar(self.database_path)), 1)

    def test_vaga_ocupada_nao_e_reutilizada(self):
        self.vaga("C1", 1)
        self.entrada("CARRO1", 1)
        with self.assertRaises(ErroEstacionamento):
            self.entrada("CARRO2", 1)
        self.assertEqual(len(movimentacoes.listar(self.database_path)), 1)

    def test_veiculo_existente_e_reutilizado(self):
        self.vaga("C1", 1)
        existente_id = veiculos.criar(
            "CARRO1", "Original", "Preto", 1, self.database_path
        )
        mov_id = registrar_entrada(
            "CARRO1", self.usuario_id, modelo="Ignorado", cor="Verde", tipo=2,
            momento=self.agora, caminho=self.database_path,
        )
        self.assertEqual(self.movimentacao(mov_id)[1], existente_id)
        self.assertEqual(len(veiculos.listar(self.database_path)), 1)
        self.assertEqual(veiculos.buscar_por_id(existente_id, self.database_path)[2:5],
                         ("Original", "Preto", 1))

    def test_nova_entrada_tem_campos_abertos_corretos(self):
        vaga_id = self.vaga("C1", 1)
        mov_id = self.entrada("CARRO1", 1)
        registro = self.movimentacao(mov_id)
        self.assertEqual(registro[2], vaga_id)
        self.assertEqual(registro[3], self.usuario_id)
        self.assertIsNone(registro[4])
        self.assertEqual(registro[5], self.agora.isoformat())
        self.assertIsNone(registro[6])
        self.assertEqual(registro[7], 0)
        self.assertIsNone(registro[8])

    def test_saida_encerra_movimentacao_registra_usuario_e_libera_vaga(self):
        vaga_id = self.vaga("C1", 1)
        mov_id = self.entrada("CARRO1", 1)
        usuario_saida_id = usuarios.criar("saida", "senha", self.database_path)
        saida = self.agora + timedelta(minutes=5)
        valor = registrar_saida(
            mov_id, usuario_saida_id, saida, self.database_path
        )
        registro = self.movimentacao(mov_id)
        self.assertEqual(valor, 10.0)
        self.assertEqual(registro[4], usuario_saida_id)
        self.assertEqual(registro[6], saida.isoformat())
        self.assertEqual(registro[8], 10.0)
        novo_mov_id = registrar_entrada(
            "CARRO2", self.usuario_id, "Outro", "Azul", 1,
            momento=saida, caminho=self.database_path,
        )
        self.assertEqual(self.movimentacao(novo_mov_id)[2], vaga_id)

    def test_saida_sem_movimentacao_aberta_falha(self):
        with self.assertRaisesRegex(ErroEstacionamento, "Não existe movimentação aberta"):
            registrar_saida(999, self.usuario_id, self.agora, self.database_path)

    def test_saida_anterior_ou_igual_a_entrada_falha_sem_alterar_movimentacao(self):
        entrada = datetime(2026, 10, 22, 14, 0)
        casos = (
            ("anterior", datetime(2026, 10, 22, 13, 0)),
            ("igual", datetime(2026, 10, 22, 14, 0)),
        )
        for identificador, saida in casos:
            with self.subTest(identificador=identificador):
                self.vaga(f"C-{identificador}", 1)
                movimentacao_id = self.entrada(
                    f"CARRO-{identificador}", 1, momento=entrada
                )
                with self.assertRaisesRegex(
                    ErroEstacionamento,
                    "horário de saída deve ser posterior",
                ):
                    registrar_saida(
                        movimentacao_id,
                        self.usuario_id,
                        saida,
                        self.database_path,
                    )

                registro = self.movimentacao(movimentacao_id)
                self.assertIsNone(registro[6])
                self.assertIsNone(registro[4])
                self.assertIsNone(registro[8])

    def test_calculo_de_cobranca_arredonda_fracao_para_cima(self):
        casos = (
            (timedelta(minutes=5), 10.0),
            (timedelta(hours=1), 10.0),
            (timedelta(hours=1, minutes=1), 20.0),
            (timedelta(hours=1, minutes=20), 20.0),
            (timedelta(hours=2, minutes=1), 30.0),
        )
        for duracao, esperado in casos:
            with self.subTest(duracao=duracao):
                self.assertEqual(
                    calcular_cobranca(self.agora, self.agora + duracao), esperado
                )


if __name__ == "__main__":
    unittest.main()
