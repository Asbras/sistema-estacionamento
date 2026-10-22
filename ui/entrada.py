"""Tela para registrar a entrada de veículos."""

import tkinter as tk
from tkinter import ttk

from services.estacionamento import (
    ErroEstacionamento,
    obter_resumo_entrada,
    registrar_entrada,
)


TIPOS_VEICULO = {"CARRO": 1, "MOTO": 2}


class EntradaFrame(ttk.Frame):
    def __init__(self, master, usuario, ao_voltar):
        super().__init__(master, padding=28)
        self.usuario = usuario
        self.ao_voltar = ao_voltar
        self.placa = tk.StringVar()
        self.modelo = tk.StringVar()
        self.cor = tk.StringVar()
        self.tipo = tk.StringVar(value="CARRO")
        self.pcd = tk.BooleanVar(value=False)
        self.mensagem = tk.StringVar()

        ttk.Label(
            self, text="Entrada de veículo", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(self, text=f"Funcionário: {usuario['username']}").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(6, 20)
        )

        campos = (
            ("Placa", self.placa),
            ("Modelo", self.modelo),
            ("Cor", self.cor),
        )
        for linha, (rotulo, variavel) in enumerate(campos, start=2):
            ttk.Label(self, text=rotulo).grid(row=linha, column=0, sticky="w", pady=4)
            entrada = ttk.Entry(self, textvariable=variavel, width=36)
            entrada.grid(row=linha, column=1, sticky="ew", pady=4)
            if rotulo == "Placa":
                self.placa_entry = entrada

        ttk.Label(self, text="Tipo do veículo").grid(
            row=5, column=0, sticky="w", pady=4
        )
        tipo_box = ttk.Combobox(
            self,
            textvariable=self.tipo,
            values=tuple(TIPOS_VEICULO),
            state="readonly",
            width=33,
        )
        tipo_box.grid(row=5, column=1, sticky="ew", pady=4)

        ttk.Checkbutton(
            self, text="Atendimento PCD", variable=self.pcd
        ).grid(row=6, column=1, sticky="w", pady=(6, 12))

        ttk.Label(self, textvariable=self.mensagem, wraplength=420).grid(
            row=7, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )
        botoes = ttk.Frame(self)
        botoes.grid(row=8, column=0, columnspan=2, sticky="ew")
        ttk.Button(botoes, text="Voltar", command=self.ao_voltar).pack(side="left")
        ttk.Button(
            botoes, text="Registrar entrada", command=self._registrar
        ).pack(side="right")

        self.columnconfigure(1, weight=1)
        self.placa_entry.focus_set()

    def _registrar(self):
        placa = self.placa.get().strip()
        modelo = self.modelo.get().strip()
        cor = self.cor.get().strip()
        if not placa or not modelo or not cor:
            self.mensagem.set("Preencha placa, modelo e cor.")
            return

        try:
            movimentacao_id = registrar_entrada(
                placa=placa,
                usuario_entrada_id=self.usuario["id"],
                modelo=modelo,
                cor=cor,
                tipo=TIPOS_VEICULO[self.tipo.get()],
                pcd=1 if self.pcd.get() else 0,
            )
            resumo = obter_resumo_entrada(movimentacao_id)
        except (ErroEstacionamento, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        except Exception:
            self.mensagem.set("Não foi possível registrar a entrada. Tente novamente.")
            return

        self.mensagem.set(
            f"Entrada registrada: placa {resumo['placa']} na vaga "
            f"{resumo['vaga_numero']}."
        )
        self._limpar_formulario()

    def _limpar_formulario(self):
        self.placa.set("")
        self.modelo.set("")
        self.cor.set("")
        self.tipo.set("CARRO")
        self.pcd.set(False)
        self.placa_entry.focus_set()
