"""Regras para gerenciamento de usuários do sistema."""

import sqlite3

from database.repositories import usuarios


class ErroUsuario(ValueError):
    """Erro de regra de negócio relacionado a usuários."""


def listar_usuarios(caminho=None, filtro_username=""):
    """Lista somente dados públicos dos usuários, com filtro opcional."""
    filtro_normalizado = (filtro_username or "").strip().casefold()
    resultado = []
    for usuario in usuarios.listar(caminho):
        if filtro_normalizado not in usuario[1].casefold():
            continue
        resultado.append(
            {
                "id": usuario[0],
                "username": usuario[1],
                "ativo": usuario[3],
                "situacao": "ATIVO" if usuario[3] == 1 else "INATIVO",
            }
        )
    return resultado


def cadastrar_usuario(username, senha, confirmacao_senha, caminho=None):
    """Cadastra usuário após confirmar a senha informada."""
    _validar_confirmacao_senha(senha, confirmacao_senha)
    try:
        return usuarios.criar(username, senha, caminho)
    except sqlite3.IntegrityError as erro:
        raise ErroUsuario("Já existe um usuário cadastrado com este nome.") from erro


def atualizar_usuario(usuario_id, username, nova_senha="", confirmacao_senha="",
                      caminho=None):
    """Atualiza username e, quando informada, substitui a senha do usuário."""
    if usuarios.buscar_por_id(usuario_id, caminho) is None:
        raise ErroUsuario("Usuário não encontrado.")

    senha = None
    if nova_senha or confirmacao_senha:
        _validar_confirmacao_senha(nova_senha, confirmacao_senha)
        senha = nova_senha

    try:
        return usuarios.atualizar(
            usuario_id, username=username, senha=senha, caminho=caminho
        )
    except sqlite3.IntegrityError as erro:
        raise ErroUsuario("Já existe um usuário cadastrado com este nome.") from erro


def definir_situacao_usuario(usuario_id, ativo, usuario_autenticado_id, caminho=None):
    """Ativa ou desativa usuário, protegendo a conta da sessão atual."""
    if usuarios.buscar_por_id(usuario_id, caminho) is None:
        raise ErroUsuario("Usuário não encontrado.")
    if ativo not in (0, 1):
        raise ValueError("ativo deve ser 0 ou 1.")
    if ativo == 0 and usuario_id == usuario_autenticado_id:
        raise ErroUsuario("Não é possível desativar o usuário autenticado.")
    return usuarios.definir_ativo(usuario_id, ativo, caminho)


def _validar_confirmacao_senha(senha, confirmacao_senha):
    if not senha or not confirmacao_senha:
        raise ErroUsuario("Informe a senha e a confirmação da senha.")
    if senha != confirmacao_senha:
        raise ErroUsuario("A senha e a confirmação devem ser iguais.")
