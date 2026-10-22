"""Tela gráfica para cadastro e manutenção das vagas."""

import tkinter as tk
from tkinter import ttk

from services.vagas import (
    ErroVaga,
    TIPOS_VAGA,
    atualizar_vaga,
    cadastrar_vaga,
    excluir_vaga,
    listar_vagas,
)


TIPOS_POR_NOME = {nome: codigo for codigo, nome in TIPOS_VAGA.items()}


class VagasFrame(ttk.Frame):
    def __init__(self, master, ao_voltar):
        super().__init__(master, padding=28)
        self.ao_voltar = ao_voltar
        self.vaga_selecionada_id = None
        self.numero = tk.StringVar()
        self.tipo = tk.StringVar(value="CARRO")
        self.mensagem = tk.StringVar()

        ttk.Label(
            self, text="Vagas", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        formulario = ttk.Frame(self)
        formulario.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(18, 12))
        ttk.Label(formulario, text="Número da vaga").grid(row=0, column=0, sticky="w")
        self.numero_entry = ttk.Entry(formulario, textvariable=self.numero, width=24)
        self.numero_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(4, 0))
        ttk.Label(formulario, text="Tipo").grid(row=0, column=1, sticky="w")
        ttk.Combobox(
            formulario,
            textvariable=self.tipo,
            values=tuple(TIPOS_POR_NOME),
            state="readonly",
            width=18,
        ).grid(row=1, column=1, sticky="ew", pady=(4, 0))
        formulario.columnconfigure(0, weight=1)

        botoes = ttk.Frame(self)
        botoes.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Button(botoes, text="Cadastrar", command=self._cadastrar).pack(side="left")
        ttk.Button(botoes, text="Atualizar", command=self._atualizar).pack(
            side="left", padx=8
        )
        ttk.Button(botoes, text="Excluir", command=self._excluir).pack(side="left")
        ttk.Button(botoes, text="Limpar", command=self._limpar_formulario).pack(
            side="left", padx=8
        )

        self.tree = ttk.Treeview(
            self,
            columns=("id", "numero", "tipo", "situacao"),
            displaycolumns=("numero", "tipo", "situacao"),
            show="headings",
            selectmode="browse",
            height=10,
        )
        self.tree.heading("numero", text="Número")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("situacao", text="Situação")
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("numero", width=160)
        self.tree.column("tipo", width=160)
        self.tree.column("situacao", width=160)
        self.tree.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._selecionar_vaga)

        ttk.Label(self, textvariable=self.mensagem, wraplength=500).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(12, 10)
        )
        ttk.Button(self, text="Voltar", command=self.ao_voltar).grid(
            row=5, column=1, sticky="e"
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self._atualizar_listagem()
        self.numero_entry.focus_set()

    def _atualizar_listagem(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for vaga in listar_vagas():
            self.tree.insert(
                "",
                "end",
                values=(vaga["id"], vaga["numero"], vaga["tipo_nome"], vaga["situacao"]),
            )

    def _selecionar_vaga(self, _evento):
        selecionados = self.tree.selection()
        if not selecionados:
            return
        valores = self.tree.item(selecionados[0], "values")
        self.vaga_selecionada_id = int(valores[0])
        self.numero.set(valores[1])
        self.tipo.set(valores[2])
        self.mensagem.set("")

    def _cadastrar(self):
        if not self.numero.get().strip():
            self.mensagem.set("Informe o número da vaga.")
            return
        try:
            cadastrar_vaga(self.numero.get().strip(), TIPOS_POR_NOME[self.tipo.get()])
        except (ErroVaga, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        self.mensagem.set("Vaga cadastrada com sucesso.")
        self._limpar_formulario()
        self._atualizar_listagem()

    def _atualizar(self):
        if self.vaga_selecionada_id is None:
            self.mensagem.set("Selecione uma vaga para atualizar.")
            return
        if not self.numero.get().strip():
            self.mensagem.set("Informe o número da vaga.")
            return
        try:
            atualizar_vaga(
                self.vaga_selecionada_id,
                self.numero.get().strip(),
                TIPOS_POR_NOME[self.tipo.get()],
            )
        except (ErroVaga, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        self.mensagem.set("Vaga atualizada com sucesso.")
        self._limpar_formulario()
        self._atualizar_listagem()

    def _excluir(self):
        if self.vaga_selecionada_id is None:
            self.mensagem.set("Selecione uma vaga para excluir.")
            return
        try:
            excluir_vaga(self.vaga_selecionada_id)
        except ErroVaga as erro:
            self.mensagem.set(str(erro))
            return
        self.mensagem.set("Vaga excluída com sucesso.")
        self._limpar_formulario()
        self._atualizar_listagem()

    def _limpar_formulario(self):
        self.vaga_selecionada_id = None
        self.numero.set("")
        self.tipo.set("CARRO")
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.numero_entry.focus_set()
