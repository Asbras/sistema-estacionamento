"""Inicialização e navegação entre Login e Menu principal."""

import tkinter as tk

from database.init_db import inicializar_banco
from ui.login import LoginFrame
from ui.menu import MenuFrame


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
        MenuFrame(self.root, usuario, ao_sair=self._mostrar_login).pack(
            fill="both", expand=True
        )


def executar():
    root = tk.Tk()
    EstacionamentoApp(root)
    root.mainloop()
