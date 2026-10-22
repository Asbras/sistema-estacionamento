"""Tela gráfica para cadastro e manutenção de usuários."""

import tkinter as tk
from tkinter import ttk

from services.usuarios import (
    ErroUsuario,
    atualizar_usuario,
    cadastrar_usuario,
    definir_situacao_usuario,
    listar_usuarios,
)


class UsuariosFrame(ttk.Frame):
    def __init__(self, master, usuario, ao_voltar):
        super().__init__(master, padding=28)
        self.usuario = usuario
        self.ao_voltar = ao_voltar
        self.usuario_selecionado_id = None
        self.filtro_username = tk.StringVar()
        self.username = tk.StringVar()
        self.senha = tk.StringVar()
        self.confirmacao_senha = tk.StringVar()
        self.mensagem = tk.StringVar()

        ttk.Label(
            self, text="Usuários", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(self, text=f"Funcionário: {usuario['username']}").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(6, 18)
        )

        filtro = ttk.LabelFrame(self, text="Filtro", padding=10)
        filtro.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        ttk.Label(filtro, text="Username").grid(row=0, column=0, sticky="w")
        filtro_entry = ttk.Entry(filtro, textvariable=self.filtro_username, width=26)
        filtro_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(4, 0))
        filtro_entry.bind("<Return>", self._filtrar_por_teclado)
        ttk.Button(filtro, text="Filtrar", command=self._atualizar_listagem).grid(
            row=1, column=1, sticky="w", padx=(0, 8), pady=(4, 0)
        )
        ttk.Button(filtro, text="Limpar filtro", command=self._limpar_filtro).grid(
            row=1, column=2, sticky="w", pady=(4, 0)
        )
        filtro.columnconfigure(0, weight=1)

        formulario = ttk.LabelFrame(self, text="Dados do usuário", padding=10)
        formulario.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        ttk.Label(formulario, text="Username").grid(row=0, column=0, sticky="w")
        self.username_entry = ttk.Entry(formulario, textvariable=self.username, width=26)
        self.username_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(4, 0))
        ttk.Label(formulario, text="Senha / nova senha").grid(row=0, column=1, sticky="w")
        ttk.Entry(formulario, textvariable=self.senha, show="*", width=26).grid(
            row=1, column=1, sticky="ew", padx=(0, 10), pady=(4, 0)
        )
        ttk.Label(formulario, text="Confirmar senha").grid(row=0, column=2, sticky="w")
        ttk.Entry(formulario, textvariable=self.confirmacao_senha, show="*", width=26).grid(
            row=1, column=2, sticky="ew", pady=(4, 0)
        )
        for coluna in range(3):
            formulario.columnconfigure(coluna, weight=1)

        ttk.Label(
            self,
            text="Ao atualizar, deixe os campos de senha vazios para mantê-la inalterada.",
        ).grid(row=4, column=0, columnspan=4, sticky="w", pady=(0, 8))

        botoes = ttk.Frame(self)
        botoes.grid(row=5, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        ttk.Button(botoes, text="Cadastrar", command=self._cadastrar).pack(side="left")
        ttk.Button(botoes, text="Atualizar", command=self._atualizar).pack(
            side="left", padx=8
        )
        ttk.Button(botoes, text="Ativar", command=lambda: self._definir_situacao(1)).pack(
            side="left"
        )
        ttk.Button(
            botoes, text="Desativar", command=lambda: self._definir_situacao(0)
        ).pack(side="left", padx=8)
        ttk.Button(botoes, text="Limpar", command=self._limpar_formulario).pack(
            side="left"
        )

        self.tree = ttk.Treeview(
            self,
            columns=("id", "username", "situacao"),
            displaycolumns=("username", "situacao"),
            show="headings",
            selectmode="browse",
            height=10,
        )
        self.tree.heading("username", text="Username")
        self.tree.heading("situacao", text="Situação")
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("username", width=290)
        self.tree.column("situacao", width=160)
        self.tree.grid(row=6, column=0, columnspan=4, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._selecionar_usuario)

        ttk.Label(self, textvariable=self.mensagem, wraplength=650).grid(
            row=7, column=0, columnspan=4, sticky="w", pady=(12, 10)
        )
        ttk.Button(self, text="Voltar", command=self.ao_voltar).grid(
            row=8, column=3, sticky="e"
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(6, weight=1)
        self._atualizar_listagem()
        self.username_entry.focus_set()

    def _filtrar_por_teclado(self, _evento):
        self._atualizar_listagem()
        return "break"

    def _atualizar_listagem(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for usuario in listar_usuarios(filtro_username=self.filtro_username.get()):
            self.tree.insert(
                "",
                "end",
                values=(usuario["id"], usuario["username"], usuario["situacao"]),
            )

    def _limpar_filtro(self):
        self.filtro_username.set("")
        self._atualizar_listagem()

    def _selecionar_usuario(self, _evento):
        selecionados = self.tree.selection()
        if not selecionados:
            return
        valores = self.tree.item(selecionados[0], "values")
        self.usuario_selecionado_id = int(valores[0])
        self.username.set(valores[1])
        self.senha.set("")
        self.confirmacao_senha.set("")
        self.mensagem.set("")

    def _cadastrar(self):
        try:
            cadastrar_usuario(
                self.username.get().strip(),
                self.senha.get(),
                self.confirmacao_senha.get(),
            )
        except (ErroUsuario, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        self.mensagem.set("Usuário cadastrado com sucesso.")
        self._limpar_formulario()
        self._atualizar_listagem()

    def _atualizar(self):
        if self.usuario_selecionado_id is None:
            self.mensagem.set("Selecione um usuário para atualizar.")
            return
        try:
            atualizar_usuario(
                self.usuario_selecionado_id,
                self.username.get().strip(),
                self.senha.get(),
                self.confirmacao_senha.get(),
            )
        except (ErroUsuario, ValueError) as erro:
            self.mensagem.set(str(erro))
            return

        if self.usuario_selecionado_id == self.usuario["id"]:
            self.usuario["username"] = self.username.get().strip()
        self.mensagem.set("Usuário atualizado com sucesso.")
        self._limpar_formulario()
        self._atualizar_listagem()

    def _definir_situacao(self, ativo):
        if self.usuario_selecionado_id is None:
            self.mensagem.set("Selecione um usuário para alterar a situação.")
            return
        try:
            definir_situacao_usuario(
                self.usuario_selecionado_id,
                ativo,
                self.usuario["id"],
            )
        except (ErroUsuario, ValueError) as erro:
            self.mensagem.set(str(erro))
            return
        situacao = "ativado" if ativo == 1 else "desativado"
        self.mensagem.set(f"Usuário {situacao} com sucesso.")
        self._limpar_formulario()
        self._atualizar_listagem()

    def _limpar_formulario(self):
        self.usuario_selecionado_id = None
        self.username.set("")
        self.senha.set("")
        self.confirmacao_senha.set("")
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.username_entry.focus_set()
