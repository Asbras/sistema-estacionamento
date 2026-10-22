"""Autenticação de funcionários sem dependência de interface gráfica."""

from database.repositories import usuarios
from database.passwords import verificar_senha


class ErroAutenticacao(ValueError):
    """Falha ao autenticar ou acesso de usuário inativo."""


def autenticar(username, senha, caminho=None):
    """Valida credenciais e retorna dados públicos do funcionário autenticado."""
    usuario = usuarios.buscar_por_username(username, caminho)
    if usuario is None:
        raise ErroAutenticacao("Usuário ou senha inválidos.")
    if usuario[3] != 1:
        raise ErroAutenticacao("Usuário inativo.")
    if not verificar_senha(senha, usuario[2]):
        raise ErroAutenticacao("Usuário ou senha inválidos.")
    return {"id": usuario[0], "username": usuario[1], "ativo": usuario[3]}
