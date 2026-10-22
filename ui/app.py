"""Inicialização e navegação entre Login e Menu principal."""

import tkinter as tk

from database.init_db import inicializar_banco
from ui.dados_importados import DadosImportadosFrame
from ui.entrada import EntradaFrame
from ui.historico import HistoricoFrame
from ui.login import LoginFrame
from ui.importacao import ImportacaoFrame
from ui.menu import MenuFrame
from ui.saida import SaidaFrame
from ui.sobre import SobreFrame
from ui.usuarios import UsuariosFrame
from ui.vagas import VagasFrame
from ui.veiculos import VeiculosFrame


class EstacionamentoApp:
    def __init__(self, root):
        inicializar_banco()
        self.root = root
        self.root.title("Sistema de Estacionamento")
        self.root.geometry("560x480")
        self.root.minsize(480, 400)
        self.usuario_autenticado = None
        self._mostrar_login()

    def _limpar_janela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _mostrar_login(self):
        self.usuario_autenticado = None
        self._limpar_janela()
        LoginFrame(self.root, ao_autenticar=self._mostrar_menu).pack(
            fill="both", expand=True
        )

    def _mostrar_menu(self, usuario):
        self.usuario_autenticado = usuario
        self._limpar_janela()
        MenuFrame(
            self.root,
            usuario,
            ao_abrir_entrada=self._mostrar_entrada,
            ao_abrir_saida=self._mostrar_saida,
            ao_abrir_veiculos=self._mostrar_veiculos,
            ao_abrir_vagas=self._mostrar_vagas,
            ao_abrir_historico=self._mostrar_historico,
            ao_abrir_usuarios=self._mostrar_usuarios,
            ao_abrir_sobre=self._mostrar_sobre,
            ao_abrir_importacao=self._mostrar_importacao,
            ao_abrir_dados_importados=self._mostrar_dados_importados,
            ao_sair=self._mostrar_login,
        ).pack(
            fill="both", expand=True
        )

    def _mostrar_entrada(self):
        self._limpar_janela()
        EntradaFrame(
            self.root,
            self.usuario_autenticado,
            ao_voltar=lambda: self._mostrar_menu(self.usuario_autenticado),
        ).pack(fill="both", expand=True)

    def _mostrar_vagas(self):
        self._limpar_janela()
        VagasFrame(
            self.root,
            ao_voltar=lambda: self._mostrar_menu(self.usuario_autenticado),
        ).pack(fill="both", expand=True)

    def _mostrar_veiculos(self):
        self._limpar_janela()
        VeiculosFrame(
            self.root,
            self.usuario_autenticado,
            ao_voltar=lambda: self._mostrar_menu(self.usuario_autenticado),
        ).pack(fill="both", expand=True)

    def _mostrar_saida(self):
        self._limpar_janela()
        SaidaFrame(
            self.root,
            self.usuario_autenticado,
            ao_voltar=lambda: self._mostrar_menu(self.usuario_autenticado),
        ).pack(fill="both", expand=True)

    def _mostrar_historico(self):
        self._limpar_janela()
        HistoricoFrame(
            self.root,
            self.usuario_autenticado,
            ao_voltar=lambda: self._mostrar_menu(self.usuario_autenticado),
        ).pack(fill="both", expand=True)

    def _mostrar_usuarios(self):
        self._limpar_janela()
        UsuariosFrame(
            self.root,
            self.usuario_autenticado,
            ao_voltar=lambda: self._mostrar_menu(self.usuario_autenticado),
        ).pack(fill="both", expand=True)

    def _mostrar_sobre(self):
        self._limpar_janela()
        SobreFrame(
            self.root,
            ao_voltar=lambda: self._mostrar_menu(self.usuario_autenticado),
        ).pack(fill="both", expand=True)

    def _mostrar_importacao(self):
        self._limpar_janela()
        ImportacaoFrame(
            self.root,
            self.usuario_autenticado,
            ao_voltar=lambda: self._mostrar_menu(self.usuario_autenticado),
        ).pack(fill="both", expand=True)

    def _mostrar_dados_importados(self):
        self._limpar_janela()
        DadosImportadosFrame(
            self.root,
            self.usuario_autenticado,
            ao_voltar=lambda: self._mostrar_menu(self.usuario_autenticado),
        ).pack(fill="both", expand=True)


def executar():
    root = tk.Tk()
    EstacionamentoApp(root)
    root.mainloop()
