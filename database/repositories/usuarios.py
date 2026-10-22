"""Acesso a dados de usuários."""

from database.passwords import eh_hash_senha, gerar_hash_senha
from database.repositories._common import (
    consultar_todos,
    consultar_um,
    executar,
    validar_categoria,
    validar_texto_obrigatorio,
)


def _preparar_senha(senha):
    # Permite repassar acidentalmente um valor lido do banco sem aplicar hash duplo.
    return senha if eh_hash_senha(senha) else gerar_hash_senha(senha)


def criar(username, senha, caminho=None):
    validar_texto_obrigatorio("username", username)
    validar_texto_obrigatorio("senha", senha)
    senha_hash = _preparar_senha(senha)
    return executar(
        "INSERT INTO usuario (username, senha) VALUES (?, ?)",
        (username, senha_hash), caminho, retornar_id=True,
    )


def buscar_por_id(usuario_id, caminho=None):
    return consultar_um("SELECT * FROM usuario WHERE id = ?", (usuario_id,), caminho)


def buscar_por_username(username, caminho=None):
    return consultar_um("SELECT * FROM usuario WHERE username = ?", (username,), caminho)


def listar(caminho=None):
    return consultar_todos("SELECT * FROM usuario ORDER BY id", caminho=caminho)


def atualizar(usuario_id, username=None, senha=None, ativo=None, caminho=None):
    alteracoes = []
    parametros = []
    if username is not None:
        validar_texto_obrigatorio("username", username)
        alteracoes.append("username = ?")
        parametros.append(username)
    if senha is not None:
        validar_texto_obrigatorio("senha", senha)
        alteracoes.append("senha = ?")
        parametros.append(_preparar_senha(senha))
    if ativo is not None:
        validar_categoria("ativo", ativo, (0, 1))
        alteracoes.append("ativo = ?")
        parametros.append(ativo)
    if not alteracoes:
        raise ValueError("Informe ao menos um campo para atualizar.")
    parametros.append(usuario_id)
    return executar(
        f"UPDATE usuario SET {', '.join(alteracoes)} WHERE id = ?",
        parametros, caminho,
    )


def definir_ativo(usuario_id, ativo, caminho=None):
    validar_categoria("ativo", ativo, (0, 1))
    return executar(
        "UPDATE usuario SET ativo = ? WHERE id = ?",
        (ativo, usuario_id), caminho,
    )
