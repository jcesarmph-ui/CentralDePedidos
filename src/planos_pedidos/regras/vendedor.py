"""Nome de quem registrou: o primeiro nome tirado do usuário do Windows.

Ex.: "joao.silva" → "JOAO". Assim ninguém precisa digitar o próprio nome (pedido do
usuário em 2026-11-18: o mais prático possível).
"""

import getpass
import re

# Separadores que aparecem nos logins: ponto, sublinhado, hífen, espaço.
_SEPARADORES = re.compile(r"[._\-\s]+")


def primeiro_nome(usuario: str) -> str:
    """Devolve só o primeiro nome, em MAIÚSCULAS, a partir do login do Windows.

    Aceita formatos com domínio ("EMPRESA\\joao.silva") ou e-mail ("joao.silva@empresa").
    Números grudados no fim ("joao2") são tirados. Login vazio vira "".
    """
    nome = usuario.strip()
    nome = nome.rsplit("\\", 1)[-1]  # tira o domínio
    nome = nome.split("@", 1)[0]  # tira o e-mail
    partes = [p for p in _SEPARADORES.split(nome) if p]
    if not partes:
        return ""
    primeiro = re.sub(r"\d+$", "", partes[0]) or partes[0]
    return primeiro.upper()


def vendedor_atual() -> str:
    """Primeiro nome de quem está usando este PC agora."""
    try:
        return primeiro_nome(getpass.getuser())
    except Exception:  # sem usuário identificável: melhor vazio do que travar o programa
        return ""
