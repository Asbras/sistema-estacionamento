"""Tela de Login, conectada ao serviço de autenticação."""

import tkinter as tk
from tkinter import ttk

from services.autenticacao import ErroAutenticacao, autenticar


class LoginFrame(ttk.Frame):
    def __init__(self, master, ao_autenticar):
        super().__init__(master, padding=32)
        self.ao_autenticar = ao_autenticar
        self.username = tk.StringVar()
        self.senha = tk.StringVar()
        self.mensagem = tk.StringVar()

        painel = ttk.Frame(self)
        painel.place(relx=0.5, rely=0.48, anchor="center")

        ttk.Label(
            painel, text="Sistema de Estacionamento", font=("TkDefaultFont", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Label(painel, text="Acesse com sua conta de funcionário.").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 24)
        )

        ttk.Label(painel, text="Usuário").grid(row=2, column=0, columnspan=2, sticky="w")
        self.username_entry = ttk.Entry(painel, textvariable=self.username, width=36)
        self.username_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 14))

        ttk.Label(painel, text="Senha").grid(row=4, column=0, columnspan=2, sticky="w")
        self.senha_entry = ttk.Entry(
            painel, textvariable=self.senha, show="*", width=36
        )
        self.senha_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(4, 14))
        self.senha_entry.bind("<Return>", self._entrar_por_teclado)

        ttk.Label(painel, textvariable=self.mensagem, foreground="#a12622").grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        ttk.Button(painel, text="Entrar", command=self._entrar).grid(
            row=7, column=0, columnspan=2, sticky="ew"
        )
        self.username_entry.focus_set()

    def _entrar_por_teclado(self, _evento):
        self._entrar()
        return "break"

    def _entrar(self):
        try:
            usuario = autenticar(self.username.get(), self.senha.get())
        except ErroAutenticacao as erro:
            self.mensagem.set(str(erro))
            self.senha.set("")
            self.senha_entry.focus_set()
            return
        self.mensagem.set("")
        self.senha.set("")
        self.ao_autenticar(usuario)
