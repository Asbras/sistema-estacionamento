"""Acesso a dados das marcas obtidas pela BrasilAPI/FIPE."""

from database.repositories._common import (
    consultar_todos,
    executar,
    validar_categoria,
    validar_texto_obrigatorio,
)


def salvar(tipo, codigo, nome, importado_em, caminho=None, conexao=None):
    """Insere uma marca, ignorando uma duplicação de tipo e código."""
    validar_categoria("tipo", tipo, (1, 2))
    validar_texto_obrigatorio("codigo", codigo)
    validar_texto_obrigatorio("nome", nome)
    validar_texto_obrigatorio("importado_em", importado_em)
    return executar(
        "INSERT OR IGNORE INTO marca_importada "
        "(tipo, codigo, nome, importado_em) VALUES (?, ?, ?, ?)",
        (tipo, codigo, nome, importado_em), caminho, conexao=conexao,
    )


def listar(tipo=None, caminho=None):
    """Lista as marcas, opcionalmente restringindo pelo tipo interno."""
    if tipo is None:
        return consultar_todos(
            "SELECT * FROM marca_importada ORDER BY tipo, nome", caminho=caminho
        )
    validar_categoria("tipo", tipo, (1, 2))
    return consultar_todos(
        "SELECT * FROM marca_importada WHERE tipo = ? ORDER BY nome",
        (tipo,), caminho,
    )


def limpar(caminho=None):
    """Remove exclusivamente os dados importados de marcas."""
    return executar("DELETE FROM marca_importada", caminho=caminho)
