"""Tela para selecionar e registrar a saída de veículos."""

import tkinter as tk
from datetime import datetime
from tkinter import ttk

from services.estacionamento import (
    ErroEstacionamento,
    listar_movimentacoes_abertas,
    obter_resumo_saida,
    registrar_saida,
)


class SaidaFrame(ttk.Frame):
    def __init__(self, master, usuario, ao_voltar):
        super().__init__(master, padding=28)
        self.usuario = usuario
        self.ao_voltar = ao_voltar
        self.filtro_placa = tk.StringVar()
        self.mensagem = tk.StringVar()
        self.movimentacao = None
        self.movimentacoes_por_id = {}
        self.detalhes = {
            nome: tk.StringVar()
            for nome in ("placa", "modelo", "vaga", "entrada")
        }

        ttk.Label(
            self, text="Saída de veículo", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(self, text=f"Funcionário: {usuario['username']}").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(6, 20)
        )

        ttk.Label(self, text="Filtrar por placa").grid(row=2, column=0, sticky="w")
        self.filtro_entry = ttk.Entry(self, textvariable=self.filtro_placa, width=30)
        self.filtro_entry.grid(row=2, column=1, sticky="ew", pady=4)
        self.filtro_entry.bind("<Return>", self._filtrar_por_teclado)
        ttk.Button(self, text="Filtrar", command=self._atualizar_lista).grid(
            row=2, column=2, padx=(8, 0), sticky="w"
        )
        ttk.Button(self, text="Limpar filtro", command=self._limpar_filtro).grid(
            row=2, column=3, padx=(8, 0), sticky="w"
        )

        lista_frame = ttk.LabelFrame(self, text="Veículos estacionados", padding=10)
        lista_frame.grid(
            row=3, column=0, columnspan=4, sticky="nsew", pady=(12, 10)
        )
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)

        self.lista = ttk.Treeview(
            lista_frame,
            columns=("placa", "modelo", "vaga", "entrada"),
            show="headings",
            height=8,
        )
        for coluna, texto, largura in (
            ("placa", "Placa", 130),
            ("modelo", "Modelo", 180),
            ("vaga", "Vaga", 90),
            ("entrada", "Entrada", 160),
        ):
            self.lista.heading(coluna, text=texto)
            self.lista.column(coluna, width=largura, anchor="center")
        self.lista.column("placa", anchor="w")
        self.lista.column("modelo", anchor="w")
        self.lista.grid(row=0, column=0, sticky="nsew")
        self.lista.bind("<<TreeviewSelect>>", self._selecionar_movimentacao)

        barra_rolagem = ttk.Scrollbar(
            lista_frame, orient="vertical", command=self.lista.yview
        )
        barra_rolagem.grid(row=0, column=1, sticky="ns")
        self.lista.configure(yscrollcommand=barra_rolagem.set)

        quadro = ttk.LabelFrame(self, text="Movimentação selecionada", padding=12)
        quadro.grid(row=4, column=0, columnspan=4, sticky="ew")
        for linha, (rotulo, chave) in enumerate(
            (("Placa", "placa"), ("Modelo", "modelo"), ("Vaga", "vaga"), ("Entrada", "entrada"))
        ):
            ttk.Label(quadro, text=f"{rotulo}:").grid(
                row=linha, column=0, sticky="w", padx=(0, 12)
            )
            ttk.Label(quadro, textvariable=self.detalhes[chave]).grid(
                row=linha, column=1, sticky="w"
            )

        self.confirmar = ttk.Button(
            self, text="Confirmar saída", command=self._confirmar, state="disabled"
        )
        self.confirmar.grid(row=5, column=2, sticky="e", pady=(14, 10))
        ttk.Button(self, text="Voltar", command=self.ao_voltar).grid(
            row=5, column=3, sticky="e", pady=(14, 10)
        )
        ttk.Label(self, textvariable=self.mensagem, wraplength=650).grid(
            row=6, column=0, columnspan=4, sticky="w", pady=(0, 10)
        )

        self.columnconfigure(1, weight=1)
        self.filtro_entry.focus_set()
        self._atualizar_lista()

    def _filtrar_por_teclado(self, _evento):
        self._atualizar_lista()
        return "break"

    def _atualizar_lista(self):
        self._limpar_movimentacao()
        self.movimentacoes_por_id = {}
        for item in self.lista.get_children():
            self.lista.delete(item)

        try:
            movimentacoes_abertas = listar_movimentacoes_abertas(
                filtro_placa=self.filtro_placa.get()
            )
        except (ErroEstacionamento, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        except Exception:
            self.mensagem.set("Não foi possível atualizar a lista de veículos estacionados.")
            return

        self.movimentacoes_por_id = {
            movimentacao["id"]: movimentacao for movimentacao in movimentacoes_abertas
        }
        for movimentacao in movimentacoes_abertas:
            self.lista.insert(
                "",
                "end",
                iid=str(movimentacao["id"]),
                values=(
                    movimentacao["placa"],
                    movimentacao["modelo"],
                    movimentacao["vaga_numero"],
                    _formatar_data_hora(movimentacao["entrada"]),
                ),
            )

        if movimentacoes_abertas:
            self.mensagem.set("Selecione um veículo para confirmar a saída.")
        else:
            self.mensagem.set("Nenhuma movimentação aberta encontrada.")

    def _limpar_filtro(self):
        self.filtro_placa.set("")
        self._atualizar_lista()

    def _selecionar_movimentacao(self, _evento):
        selecionados = self.lista.selection()
        if not selecionados:
            self._limpar_movimentacao()
            return

        movimentacao_id = int(selecionados[0])
        self.movimentacao = self.movimentacoes_por_id[movimentacao_id]
        self.detalhes["placa"].set(self.movimentacao["placa"])
        self.detalhes["modelo"].set(self.movimentacao["modelo"])
        self.detalhes["vaga"].set(self.movimentacao["vaga_numero"])
        self.detalhes["entrada"].set(_formatar_data_hora(self.movimentacao["entrada"]))
        self.mensagem.set("Movimentação selecionada. Confirme a saída para encerrar.")
        self.confirmar.configure(state="normal")

    def _confirmar(self):
        if self.movimentacao is None:
            self.mensagem.set("Selecione um veículo antes de confirmar a saída.")
            return
        try:
            registrar_saida(self.movimentacao["id"], self.usuario["id"])
            resumo = obter_resumo_saida(self.movimentacao["id"])
        except (ErroEstacionamento, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        except Exception:
            self.mensagem.set("Não foi possível registrar a saída. Tente novamente.")
            return

        mensagem = (
            f"Saída registrada: placa {resumo['placa']}, vaga {resumo['vaga_numero']}, "
            f"entrada {_formatar_data_hora(resumo['entrada'])}, "
            f"saída {_formatar_data_hora(resumo['saida'])}. "
            f"Valor: R$ {_formatar_valor(resumo['valor'])}"
        )
        self._atualizar_lista()
        self.mensagem.set(mensagem)

    def _limpar_movimentacao(self):
        self.movimentacao = None
        self.confirmar.configure(state="disabled")
        for variavel in self.detalhes.values():
            variavel.set("")


def _formatar_data_hora(valor):
    try:
        return datetime.fromisoformat(valor).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return valor or ""


def _formatar_valor(valor):
    return f"{valor:.2f}".replace(".", ",")
