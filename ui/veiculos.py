"""Tela gráfica para cadastro e manutenção de veículos."""

import tkinter as tk
from tkinter import ttk

from services.veiculos import (
    ErroVeiculo,
    TIPOS_VEICULO,
    atualizar_veiculo,
    cadastrar_veiculo,
    excluir_veiculo,
    listar_veiculos,
)


TIPOS_POR_NOME = {nome: codigo for codigo, nome in TIPOS_VEICULO.items()}


class VeiculosFrame(ttk.Frame):
    def __init__(self, master, usuario, ao_voltar):
        super().__init__(master, padding=28)
        self.usuario = usuario
        self.ao_voltar = ao_voltar
        self.veiculo_selecionado_id = None
        self.filtro_placa = tk.StringVar()
        self.placa = tk.StringVar()
        self.modelo = tk.StringVar()
        self.cor = tk.StringVar()
        self.tipo = tk.StringVar(value="CARRO")
        self.mensagem = tk.StringVar()

        ttk.Label(
            self, text="Veículos", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(self, text=f"Funcionário: {usuario['username']}").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(6, 18)
        )

        filtro = ttk.LabelFrame(self, text="Filtro", padding=10)
        filtro.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        ttk.Label(filtro, text="Placa").grid(row=0, column=0, sticky="w")
        filtro_entry = ttk.Entry(filtro, textvariable=self.filtro_placa, width=24)
        filtro_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(4, 0))
        filtro_entry.bind("<Return>", self._filtrar_por_teclado)
        ttk.Button(filtro, text="Filtrar", command=self._atualizar_listagem).grid(
            row=1, column=1, sticky="w", padx=(0, 8), pady=(4, 0)
        )
        ttk.Button(filtro, text="Limpar filtro", command=self._limpar_filtro).grid(
            row=1, column=2, sticky="w", pady=(4, 0)
        )
        filtro.columnconfigure(0, weight=1)

        formulario = ttk.LabelFrame(self, text="Dados do veículo", padding=10)
        formulario.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        campos = (
            ("Placa", self.placa),
            ("Modelo", self.modelo),
            ("Cor", self.cor),
        )
        for coluna, (rotulo, variavel) in enumerate(campos):
            ttk.Label(formulario, text=rotulo).grid(row=0, column=coluna, sticky="w")
            entrada = ttk.Entry(formulario, textvariable=variavel, width=22)
            entrada.grid(row=1, column=coluna, sticky="ew", padx=(0, 10), pady=(4, 0))
            if rotulo == "Placa":
                self.placa_entry = entrada
            formulario.columnconfigure(coluna, weight=1)
        ttk.Label(formulario, text="Tipo").grid(row=0, column=3, sticky="w")
        ttk.Combobox(
            formulario,
            textvariable=self.tipo,
            values=tuple(TIPOS_POR_NOME),
            state="readonly",
            width=16,
        ).grid(row=1, column=3, sticky="ew", pady=(4, 0))

        botoes = ttk.Frame(self)
        botoes.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(0, 12))
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
            columns=("id", "placa", "modelo", "cor", "tipo"),
            displaycolumns=("placa", "modelo", "cor", "tipo"),
            show="headings",
            selectmode="browse",
            height=10,
        )
        for coluna, texto, largura in (
            ("placa", "Placa", 140),
            ("modelo", "Modelo", 180),
            ("cor", "Cor", 140),
            ("tipo", "Tipo", 120),
        ):
            self.tree.heading(coluna, text=texto)
            self.tree.column(coluna, width=largura)
        self.tree.column("id", width=0, stretch=False)
        self.tree.grid(row=5, column=0, columnspan=4, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._selecionar_veiculo)

        ttk.Label(self, textvariable=self.mensagem, wraplength=650).grid(
            row=6, column=0, columnspan=4, sticky="w", pady=(12, 10)
        )
        ttk.Button(self, text="Voltar", command=self.ao_voltar).grid(
            row=7, column=3, sticky="e"
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)
        self._atualizar_listagem()
        self.placa_entry.focus_set()

    def _filtrar_por_teclado(self, _evento):
        self._atualizar_listagem()
        return "break"

    def _atualizar_listagem(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for veiculo in listar_veiculos(filtro_placa=self.filtro_placa.get()):
            self.tree.insert(
                "",
                "end",
                values=(
                    veiculo["id"],
                    veiculo["placa"],
                    veiculo["modelo"],
                    veiculo["cor"],
                    veiculo["tipo_nome"],
                ),
            )

    def _limpar_filtro(self):
        self.filtro_placa.set("")
        self._atualizar_listagem()

    def _selecionar_veiculo(self, _evento):
        selecionados = self.tree.selection()
        if not selecionados:
            return
        valores = self.tree.item(selecionados[0], "values")
        self.veiculo_selecionado_id = int(valores[0])
        self.placa.set(valores[1])
        self.modelo.set(valores[2])
        self.cor.set(valores[3])
        self.tipo.set(valores[4])
        self.mensagem.set("")

    def _dados_formulario(self):
        return (
            self.placa.get().strip(),
            self.modelo.get().strip(),
            self.cor.get().strip(),
            TIPOS_POR_NOME[self.tipo.get()],
        )

    def _cadastrar(self):
        try:
            cadastrar_veiculo(*self._dados_formulario())
        except (ErroVeiculo, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        self.mensagem.set("Veículo cadastrado com sucesso.")
        self._limpar_formulario()
        self._atualizar_listagem()

    def _atualizar(self):
        if self.veiculo_selecionado_id is None:
            self.mensagem.set("Selecione um veículo para atualizar.")
            return
        try:
            atualizar_veiculo(self.veiculo_selecionado_id, *self._dados_formulario())
        except (ErroVeiculo, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        self.mensagem.set("Veículo atualizado com sucesso.")
        self._limpar_formulario()
        self._atualizar_listagem()

    def _excluir(self):
        if self.veiculo_selecionado_id is None:
            self.mensagem.set("Selecione um veículo para excluir.")
            return
        try:
            excluir_veiculo(self.veiculo_selecionado_id)
        except ErroVeiculo as erro:
            self.mensagem.set(str(erro))
            return
        self.mensagem.set("Veículo excluído com sucesso.")
        self._limpar_formulario()
        self._atualizar_listagem()

    def _limpar_formulario(self):
        self.veiculo_selecionado_id = None
        self.placa.set("")
        self.modelo.set("")
        self.cor.set("")
        self.tipo.set("CARRO")
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.placa_entry.focus_set()
