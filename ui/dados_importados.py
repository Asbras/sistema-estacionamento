"""Tela de consulta e limpeza das marcas importadas."""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from services.importacao import limpar_marcas_importadas, listar_marcas_importadas


TIPOS_FILTRO = {"TODOS": None, "CARRO": 1, "MOTO": 2}


class DadosImportadosFrame(ttk.Frame):
    def __init__(self, master, usuario, ao_voltar):
        super().__init__(master, padding=28)
        self.usuario = usuario
        self.ao_voltar = ao_voltar
        self.tipo = tk.StringVar(value="TODOS")
        self.nome = tk.StringVar()
        self.mensagem = tk.StringVar()

        ttk.Label(
            self, text="Dados importados", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, columnspan=5, sticky="w")
        ttk.Label(self, text=f"Funcionário: {usuario['username']}").grid(
            row=1, column=0, columnspan=5, sticky="w", pady=(6, 18)
        )

        filtros = ttk.LabelFrame(self, text="Filtros", padding=10)
        filtros.grid(row=2, column=0, columnspan=5, sticky="ew", pady=(0, 12))
        ttk.Label(filtros, text="Tipo").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            filtros,
            textvariable=self.tipo,
            values=tuple(TIPOS_FILTRO),
            state="readonly",
            width=14,
        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(4, 0))
        ttk.Label(filtros, text="Nome da marca").grid(row=0, column=1, sticky="w")
        nome_entry = ttk.Entry(filtros, textvariable=self.nome, width=28)
        nome_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(4, 0))
        nome_entry.bind("<Return>", self._atualizar_por_teclado)
        ttk.Button(filtros, text="Atualizar", command=self._atualizar_listagem).grid(
            row=1, column=2, padx=(0, 8), pady=(4, 0), sticky="w"
        )
        ttk.Button(filtros, text="Limpar filtros", command=self._limpar_filtros).grid(
            row=1, column=3, pady=(4, 0), sticky="w"
        )
        filtros.columnconfigure(1, weight=1)

        self.tree = ttk.Treeview(
            self,
            columns=("tipo", "codigo", "nome", "importado_em"),
            show="headings",
            height=12,
        )
        for coluna, texto, largura in (
            ("tipo", "Tipo", 100),
            ("codigo", "Código", 100),
            ("nome", "Marca", 260),
            ("importado_em", "Importado em", 170),
        ):
            self.tree.heading(coluna, text=texto)
            self.tree.column(coluna, width=largura)
        self.tree.grid(row=3, column=0, columnspan=5, sticky="nsew")

        botoes = ttk.Frame(self)
        botoes.grid(row=4, column=0, columnspan=5, sticky="ew", pady=(12, 0))
        ttk.Button(
            botoes, text="Limpar dados importados", command=self._confirmar_limpeza
        ).pack(side="left")
        ttk.Button(botoes, text="Voltar", command=self.ao_voltar).pack(side="right")
        ttk.Label(self, textvariable=self.mensagem, wraplength=650).grid(
            row=5, column=0, columnspan=5, sticky="w", pady=(10, 0)
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        nome_entry.focus_set()
        self._atualizar_listagem()

    def _atualizar_por_teclado(self, _evento):
        self._atualizar_listagem()
        return "break"

    def _atualizar_listagem(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        marcas = listar_marcas_importadas(
            tipo=TIPOS_FILTRO[self.tipo.get()], filtro_nome=self.nome.get()
        )
        for marca in marcas:
            self.tree.insert(
                "",
                "end",
                values=(
                    marca["tipo_nome"],
                    marca["codigo"],
                    marca["nome"],
                    _formatar_data_hora(marca["importado_em"]),
                ),
            )
        self.mensagem.set(f"{len(marcas)} marca(s) encontrada(s).")

    def _limpar_filtros(self):
        self.tipo.set("TODOS")
        self.nome.set("")
        self._atualizar_listagem()

    def _confirmar_limpeza(self):
        if not messagebox.askyesno(
            "Limpar dados importados",
            "Deseja remover todas as marcas importadas? Veículos, vagas, usuários "
            "e movimentações não serão alterados.",
            parent=self.winfo_toplevel(),
        ):
            return
        removidas = limpar_marcas_importadas()
        self._atualizar_listagem()
        self.mensagem.set(f"{removidas} marca(s) importada(s) removida(s).")


def _formatar_data_hora(valor):
    try:
        return datetime.fromisoformat(valor).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return valor or ""
