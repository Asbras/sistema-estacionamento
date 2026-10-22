"""Utilitários compartilhados pelos repositórios SQLite."""

from database.connection import conectar


def validar_texto_obrigatorio(campo, valor):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} é obrigatório.")


def validar_categoria(campo, valor, permitidos):
    if isinstance(valor, bool) or valor not in permitidos:
        opcoes = ", ".join(str(opcao) for opcao in permitidos)
        raise ValueError(f"{campo} deve ser um dos valores: {opcoes}.")


def executar(sql, parametros=(), caminho=None, retornar_id=False, conexao=None):
    if conexao is not None:
        cursor = conexao.execute(sql, parametros)
        return cursor.lastrowid if retornar_id else cursor.rowcount

    conexao = conectar(caminho)
    try:
        cursor = conexao.execute(sql, parametros)
        conexao.commit()
        if retornar_id:
            return cursor.lastrowid
        return cursor.rowcount
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def consultar_um(sql, parametros=(), caminho=None, conexao=None):
    if conexao is not None:
        return conexao.execute(sql, parametros).fetchone()

    conexao = conectar(caminho)
    try:
        return conexao.execute(sql, parametros).fetchone()
    finally:
        conexao.close()


def consultar_todos(sql, parametros=(), caminho=None, conexao=None):
    if conexao is not None:
        return conexao.execute(sql, parametros).fetchall()

    conexao = conectar(caminho)
    try:
        return conexao.execute(sql, parametros).fetchall()
    finally:
        conexao.close()
