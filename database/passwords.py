"""Geração e verificação de hashes de senha com recursos da biblioteca padrão."""

import hashlib
import hmac
import secrets


ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000
TAMANHO_SALT = 16
TAMANHO_HASH = 32


def gerar_hash_senha(senha):
    """Gera um hash PBKDF2 com salt aleatório e formato autocontido."""
    if not isinstance(senha, str) or not senha:
        raise ValueError("A senha é obrigatória.")
    salt = secrets.token_bytes(TAMANHO_SALT)
    derivado = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, ITERACOES, dklen=TAMANHO_HASH
    )
    return f"{ALGORITMO}${ITERACOES}${salt.hex()}${derivado.hex()}"


def eh_hash_senha(valor):
    """Indica se o texto tem a estrutura de um hash produzido por este módulo."""
    if not isinstance(valor, str):
        return False
    try:
        algoritmo, iteracoes_texto, salt_hex, hash_hex = valor.split("$")
        iteracoes = int(iteracoes_texto)
        salt = bytes.fromhex(salt_hex)
        derivado = bytes.fromhex(hash_hex)
    except (ValueError, TypeError):
        return False
    return (
        algoritmo == ALGORITMO
        and iteracoes > 0
        and len(salt) == TAMANHO_SALT
        and len(derivado) == TAMANHO_HASH
    )


def verificar_senha(senha, valor_armazenado):
    """Compara uma senha em texto com o hash armazenado; entradas inválidas falham."""
    if not isinstance(senha, str) or not isinstance(valor_armazenado, str):
        return False
    try:
        algoritmo, iteracoes_texto, salt_hex, hash_hex = valor_armazenado.split("$")
        if algoritmo != ALGORITMO:
            return False
        iteracoes = int(iteracoes_texto)
        salt = bytes.fromhex(salt_hex)
        esperado = bytes.fromhex(hash_hex)
        if iteracoes <= 0 or not salt or not esperado:
            return False
        calculado = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), salt, iteracoes,
            dklen=len(esperado),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(calculado, esperado)
