"""Tela informativa sobre o Sistema de Estacionamento."""

from tkinter import ttk


NOME_DESENVOLVEDOR = "LEONARDO CANIO DELLA TORRE"
MATRICULA_DESENVOLVEDOR = "2840482221043"
OBJETIVO_SISTEMA = (
    "Sistema desenvolvido para controlar veículos, vagas e movimentações de "
    "entrada e saída em um estacionamento de pequeno porte, incluindo controle "
    "de acesso de funcionários e cálculo do valor da permanência."
)


class SobreFrame(ttk.Frame):
    """Apresenta informações acadêmicas e funcionais do projeto."""

    def __init__(self, master, ao_voltar):
        super().__init__(master, padding=28)
        self.ao_voltar = ao_voltar

        ttk.Label(
            self, text="Sobre", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, sticky="w")

        informacoes = ttk.LabelFrame(self, text="Sistema de Estacionamento", padding=16)
        informacoes.grid(row=1, column=0, sticky="nsew", pady=(18, 16))
        informacoes.columnconfigure(0, weight=1)

        ttk.Label(informacoes, text="Tema", font=("TkDefaultFont", 10, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            informacoes, text="Controle de estacionamento de pequeno porte", wraplength=500
        ).grid(row=1, column=0, sticky="w", pady=(2, 14))

        ttk.Label(
            informacoes, text="Objetivo", font=("TkDefaultFont", 10, "bold")
        ).grid(row=2, column=0, sticky="w")
        ttk.Label(informacoes, text=OBJETIVO_SISTEMA, wraplength=500, justify="left").grid(
            row=3, column=0, sticky="w", pady=(2, 14)
        )

        ttk.Label(
            informacoes, text="Desenvolvedor", font=("TkDefaultFont", 10, "bold")
        ).grid(row=4, column=0, sticky="w")
        ttk.Label(informacoes, text=f"Nome: {NOME_DESENVOLVEDOR}").grid(
            row=5, column=0, sticky="w", pady=(2, 2)
        )
        ttk.Label(informacoes, text=f"Matrícula: {MATRICULA_DESENVOLVEDOR}").grid(
            row=6, column=0, sticky="w"
        )

        ttk.Button(self, text="Voltar", command=self.ao_voltar).grid(
            row=2, column=0, sticky="e"
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
