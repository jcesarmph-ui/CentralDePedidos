"""Testes do nome de quem registrou (primeiro nome do usuário do Windows)."""

import pytest

from planos_pedidos.regras.vendedor import primeiro_nome


@pytest.mark.parametrize(
    ("usuario", "esperado"),
    [
        ("joao.silva", "JOAO"),  # o formato mais comum: nome.sobrenome
        ("JOAO.SILVA", "JOAO"),
        ("joao_silva", "JOAO"),
        ("joao-silva", "JOAO"),
        ("Joao Silva", "JOAO"),
        ("joao", "JOAO"),
        ("EMPRESA\\joao.silva", "JOAO"),  # com domínio na frente
        ("joao.silva@empresa.com.br", "JOAO"),  # formato de e-mail
        ("joao2", "JOAO"),  # número grudado no fim
        ("  joao.silva  ", "JOAO"),
        (".joao", "JOAO"),
        ("", ""),
    ],
)
def test_primeiro_nome(usuario, esperado):
    assert primeiro_nome(usuario) == esperado
