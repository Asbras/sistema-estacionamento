"""Tela para exportar os dados persistidos para JSON e ZIP."""

import tkinter as tk
from tkinter import ttk

from services.exportacao import ErroExportacao, exportar_dados


class ExportacaoFrame(ttk.Frame):
    def __init__(self, master, usuario, ao_voltar):
        super().__init__(master, padding=28)
        self.usuario = usuario
        self.ao_voltar = ao_voltar
        self.mensagem = tk.StringVar()

        ttk.Label(
            self, text="Exportar dados", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(self, text=f"Funcionário: {usuario['username']}").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(6, 18)
        )
        ttk.Label(
            self,
            text=(
                "Todos os dados da aplicação serão exportados para um arquivo JSON "
                "e compactados em um arquivo ZIP."
            ),
            justify="left",
            wraplength=500,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 18))

        ttk.Button(self, text="Exportar", command=self._exportar).grid(
            row=3, column=0, sticky="w"
        )
        ttk.Label(self, textvariable=self.mensagem, wraplength=500).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(18, 12)
        )
        ttk.Button(self, text="Voltar", command=self.ao_voltar).grid(
            row=5, column=1, sticky="e"
        )
        self.columnconfigure(0, weight=1)

    def _exportar(self):
        try:
            resultado = exportar_dados()
        except ErroExportacao as erro:
            self.mensagem.set(str(erro))
            return
        self.mensagem.set(
            f"Exportação concluída. ZIP salvo em: {resultado['zip']}\n"
            f"JSON salvo em: {resultado['json']}"
        )
