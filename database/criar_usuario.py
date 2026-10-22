"""Cadastro interativo e explícito do primeiro usuário ou de outro funcionário."""

import getpass
import sqlite3

from database.init_db import inicializar_banco
from database.repositories import usuarios


def main():
    inicializar_banco()
    username = input("Nome de usuário: ").strip()
    senha = getpass.getpass("Senha: ")
    confirmacao = getpass.getpass("Confirme a senha: ")

    if not username:
        print("O nome de usuário é obrigatório.")
        return 1
    if senha != confirmacao:
        print("As senhas não coincidem.")
        return 1

    try:
        usuarios.criar(username, senha)
    except sqlite3.IntegrityError:
        print("Não foi possível cadastrar: o nome de usuário já existe.")
        return 1
    except ValueError as erro:
        print(erro)
        return 1

    print(f"Usuário '{username}' cadastrado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
