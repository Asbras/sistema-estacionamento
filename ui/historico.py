"""Tela de consulta ao histórico de movimentações."""

import tkinter as tk
from datetime import datetime
from tkinter import ttk

from services.estacionamento import listar_historico_movimentacoes


SITUACOES = ("TODAS", "ABERTAS", "ENCERRADAS")


class HistoricoFrame(ttk.Frame):
    def __init__(self, master, usuario, ao_voltar):
        super().__init__(master, padding=28)
        self.usuario = usuario
        self.ao_voltar = ao_voltar
        self.filtro_placa = tk.StringVar()
        self.filtro_situacao = tk.StringVar(value="TODAS")
        self.mensagem = tk.StringVar()

        ttk.Label(
            self, text="Histórico de movimentações", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, columnspan=5, sticky="w")
        ttk.Label(self, text=f"Funcionário: {usuario['username']}").grid(
            row=1, column=0, columnspan=5, sticky="w", pady=(6, 20)
        )

        filtros = ttk.LabelFrame(self, text="Filtros", padding=10)
        filtros.grid(row=2, column=0, columnspan=5, sticky="ew", pady=(0, 12))
        ttk.Label(filtros, text="Placa").grid(row=0, column=0, sticky="w")
        placa_entry = ttk.Entry(filtros, textvariable=self.filtro_placa, width=24)
        placa_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(4, 0))
        placa_entry.bind("<Return>", self._atualizar_por_teclado)
        ttk.Label(filtros, text="Situação").grid(row=0, column=1, sticky="w")
        ttk.Combobox(
            filtros,
            textvariable=self.filtro_situacao,
            values=SITUACOES,
            state="readonly",
            width=16,
        ).grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(4, 0))
        ttk.Button(filtros, text="Atualizar", command=self._atualizar_listagem).grid(
            row=1, column=2, padx=(0, 8), pady=(4, 0), sticky="w"
        )
        ttk.Button(filtros, text="Limpar filtros", command=self._limpar_filtros).grid(
            row=1, column=3, pady=(4, 0), sticky="w"
        )
        filtros.columnconfigure(0, weight=1)

        lista_frame = ttk.Frame(self)
        lista_frame.grid(row=3, column=0, columnspan=5, sticky="nsew")
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(
            lista_frame,
            columns=(
                "placa", "modelo", "vaga", "funcionario_entrada", "entrada",
                "funcionario_saida", "saida", "situacao", "valor",
            ),
            show="headings",
            height=14,
        )
        for coluna, texto, largura in (
            ("placa", "Placa", 110),
            ("modelo", "Modelo", 140),
            ("vaga", "Vaga", 70),
            ("funcionario_entrada", "Funcionário entrada", 140),
            ("entrada", "Entrada", 135),
            ("funcionario_saida", "Funcionário saída", 140),
            ("saida", "Saída", 135),
            ("situacao", "Situação", 95),
            ("valor", "Valor", 90),
        ):
            self.tree.heading(coluna, text=texto)
            self.tree.column(coluna, width=largura, anchor="center", stretch=False)
        self.tree.column("placa", anchor="w")
        self.tree.column("modelo", anchor="w")
        self.tree.column("funcionario_entrada", anchor="w")
        self.tree.column("funcionario_saida", anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        barra_vertical = ttk.Scrollbar(
            lista_frame, orient="vertical", command=self.tree.yview
        )
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal = ttk.Scrollbar(
            lista_frame, orient="horizontal", command=self.tree.xview
        )
        barra_horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set,
        )

        ttk.Label(self, textvariable=self.mensagem, wraplength=900).grid(
            row=4, column=0, columnspan=5, sticky="w", pady=(12, 10)
        )
        ttk.Button(self, text="Voltar", command=self.ao_voltar).grid(
            row=5, column=4, sticky="e"
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        placa_entry.focus_set()
        self._atualizar_listagem()

    def _atualizar_por_teclado(self, _evento):
        self._atualizar_listagem()
        return "break"

    def _atualizar_listagem(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            movimentacoes = listar_historico_movimentacoes(
                filtro_placa=self.filtro_placa.get(),
                situacao=self.filtro_situacao.get(),
            )
        except ValueError as erro:
            self.mensagem.set(str(erro))
            return
        except Exception:
            self.mensagem.set("Não foi possível carregar o histórico. Tente novamente.")
            return

        for movimentacao in movimentacoes:
            self.tree.insert(
                "",
                "end",
                values=(
                    movimentacao["placa"],
                    movimentacao["modelo"],
                    movimentacao["vaga_numero"],
                    movimentacao["funcionario_entrada"],
                    _formatar_data_hora(movimentacao["entrada"]),
                    movimentacao["funcionario_saida"] or "-",
                    _formatar_data_hora(movimentacao["saida"]),
                    movimentacao["situacao"],
                    _formatar_valor(movimentacao["valor"]),
                ),
            )

        if movimentacoes:
            self.mensagem.set(f"{len(movimentacoes)} movimentação(ões) encontrada(s).")
        else:
            self.mensagem.set("Nenhuma movimentação encontrada.")

    def _limpar_filtros(self):
        self.filtro_placa.set("")
        self.filtro_situacao.set("TODAS")
        self._atualizar_listagem()


def _formatar_data_hora(valor):
    if valor is None:
        return "-"
    try:
        return datetime.fromisoformat(valor).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return valor


def _formatar_valor(valor):
    if valor is None:
        return "-"
    return f"R$ {valor:.2f}".replace(".", ",")
