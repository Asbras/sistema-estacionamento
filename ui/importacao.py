"""Tela para importar marcas FIPE da BrasilAPI."""

import tkinter as tk
from tkinter import ttk

from services.importacao import ErroImportacao, importar_carros_e_motos, importar_marcas


class ImportacaoFrame(ttk.Frame):
    def __init__(self, master, usuario, ao_voltar):
        super().__init__(master, padding=28)
        self.usuario = usuario
        self.ao_voltar = ao_voltar
        self.mensagem = tk.StringVar()

        ttk.Label(
            self, text="Importar dados", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(self, text=f"Funcionário: {usuario['username']}").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(6, 18)
        )
        ttk.Label(
            self,
            text=(
                "Importe marcas de veículos da Tabela FIPE disponibilizadas pela "
                "BrasilAPI. Apenas carros e motos fazem parte deste projeto."
            ),
            justify="left",
            wraplength=500,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 16))

        botoes = ttk.LabelFrame(self, text="Importação de marcas", padding=14)
        botoes.grid(row=3, column=0, columnspan=2, sticky="ew")
        ttk.Button(
            botoes, text="Importar marcas de CARROS", command=lambda: self._importar("carros")
        ).grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(
            botoes, text="Importar marcas de MOTOS", command=lambda: self._importar("motos")
        ).grid(row=1, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(
            botoes, text="Importar CARROS e MOTOS", command=self._importar_ambos
        ).grid(row=2, column=0, sticky="ew")
        botoes.columnconfigure(0, weight=1)

        ttk.Label(self, textvariable=self.mensagem, wraplength=500).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(16, 12)
        )
        ttk.Button(self, text="Voltar", command=self.ao_voltar).grid(
            row=5, column=1, sticky="e"
        )

        self.columnconfigure(0, weight=1)

    def _importar(self, tipo_web):
        try:
            resultado = importar_marcas(tipo_web)
        except (ErroImportacao, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        self.mensagem.set(_mensagem_resultado(resultado))

    def _importar_ambos(self):
        try:
            resultados = importar_carros_e_motos()
        except (ErroImportacao, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        self.mensagem.set("\n".join(_mensagem_resultado(resultado) for resultado in resultados))


def _mensagem_resultado(resultado):
    return (
        f"{resultado['tipo']}: {resultado['recebidos']} registro(s) recebido(s), "
        f"{resultado['salvos']} novo(s) registro(s) salvo(s)."
    )
