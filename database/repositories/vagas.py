"""Acesso a dados de vagas."""

from database.repositories._common import (
    consultar_todos,
    consultar_um,
    executar,
    validar_categoria,
    validar_texto_obrigatorio,
)


def criar(numero, tipo, caminho=None):
    validar_texto_obrigatorio("numero", numero)
    validar_categoria("tipo", tipo, (1, 2, 3))
    return executar(
        "INSERT INTO vaga (numero, tipo) VALUES (?, ?)",
        (numero, tipo), caminho, retornar_id=True,
    )


def buscar_por_id(vaga_id, caminho=None):
    return consultar_um("SELECT * FROM vaga WHERE id = ?", (vaga_id,), caminho)


def buscar_por_numero(numero, caminho=None):
    return consultar_um("SELECT * FROM vaga WHERE numero = ?", (numero,), caminho)


def listar(caminho=None):
    return consultar_todos("SELECT * FROM vaga ORDER BY id", caminho=caminho)


def buscar_livres_por_tipo(tipo, caminho=None, conexao=None):
    """Lista vagas do tipo informado sem movimentação aberta."""
    return consultar_todos(
        "SELECT vaga.* FROM vaga "
        "WHERE vaga.tipo = ? AND NOT EXISTS ("
        "SELECT 1 FROM movimentacao "
        "WHERE movimentacao.vaga_id = vaga.id AND movimentacao.saida IS NULL"
        ") ORDER BY vaga.id",
        (tipo,), caminho, conexao,
    )


def atualizar(vaga_id, numero=None, tipo=None, caminho=None):
    alteracoes = []
    parametros = []
    if numero is not None:
        validar_texto_obrigatorio("numero", numero)
        alteracoes.append("numero = ?")
        parametros.append(numero)
    if tipo is not None:
        validar_categoria("tipo", tipo, (1, 2, 3))
        alteracoes.append("tipo = ?")
        parametros.append(tipo)
    if not alteracoes:
        raise ValueError("Informe ao menos um campo para atualizar.")
    parametros.append(vaga_id)
    return executar(
        f"UPDATE vaga SET {', '.join(alteracoes)} WHERE id = ?",
        parametros, caminho,
    )


def excluir(vaga_id, caminho=None):
    return executar("DELETE FROM vaga WHERE id = ?", (vaga_id,), caminho)
