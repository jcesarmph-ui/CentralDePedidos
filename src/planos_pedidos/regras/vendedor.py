"""Nome de quem registrou: o primeiro nome tirado do usuário do Windows.

Ex.: "joao.silva" → "JOAO". Assim ninguém precisa digitar o próprio nome (pedido do
usuário em 2026-11-18: o mais prático possível).
"""

import getpass
import os
import re
import socket
from pathlib import Path

# Quem aparece no filtro "Registrado por" quando a pasta de dados não tem a lista
# `vendedores.txt` (configurável em cada instalação).
VENDEDORES = ("ANA", "CARLOS")

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
    """Primeiro nome de quem está usando este PC agora.

    `PLANOS_PEDIDOS_USUARIO` troca o nome (usado na demonstração, para abrir "como" uma das
    vendedoras)."""
    if os.environ.get("PLANOS_PEDIDOS_USUARIO"):
        return primeiro_nome(os.environ["PLANOS_PEDIDOS_USUARIO"])
    try:
        return primeiro_nome(getpass.getuser())
    except Exception:  # sem usuário identificável: melhor vazio do que travar o programa
        return ""


def nome_pc() -> str:
    """Nome do computador (aparece no aviso de quem está editando)."""
    try:
        return socket.gethostname().upper()
    except Exception:
        return ""


def filtrar_por_vendedor(registros: list, vendedor: str) -> list:
    """Só os registrados por `vendedor` (vazio = todos). Qualquer objeto com `.vendedor`."""
    if not vendedor:
        return list(registros)
    return [r for r in registros if r.vendedor.upper() == vendedor.upper()]


def ler_vendedores(arquivo: Path) -> tuple[str, ...]:
    """Nomes do filtro, um por linha, em MAIÚSCULAS; sem a lista, os nomes de exemplo."""
    if arquivo.exists():
        nomes = [n.strip().upper() for n in arquivo.read_text(encoding="utf-8").splitlines()]
        if any(nomes):
            return tuple(n for n in nomes if n)
    return VENDEDORES
