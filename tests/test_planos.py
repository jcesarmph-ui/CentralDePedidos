import datetime

import pytest

from planos_pedidos.regras.planos import (
    Plano,
    problemas_do_plano,
    quantidade_kg,
    quantidade_tela,
)


@pytest.mark.parametrize(
    ("texto", "kg_", "tela"),
    [("2000", 2000, "2.000 kg"), ("2.500", 2500, "2.500 kg"), ("8.000kg", 8000, "8.000 kg"),
     ("12.000 kg", 12000, "12.000 kg"), ("1 un", None, "1 un"),
     ("saldo total", None, "saldo total")],
)
def test_quantidade(texto, kg_, tela):
    assert quantidade_kg(texto) == kg_
    assert quantidade_tela(texto) == tela


def test_problemas_do_plano():
    assert "Falta a descrição do item." in problemas_do_plano(Plano())
    hoje = datetime.date(2026, 11, 18)
    bom = Plano(data=hoje, cliente="Alfa Chapas", descricao="CHAPA 1,5 x 1200 x 3000",
                quantidade="saldo total", entrega=hoje)
    assert problemas_do_plano(bom) == []
