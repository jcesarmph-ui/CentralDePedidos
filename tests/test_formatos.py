import datetime

import pytest

from planos_pedidos.regras.formatos import chave, dinheiro, kg, ler_data, ler_numero, medida


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [("5.000", 5000), ("0,75", 0.75), ("1.350,50", 1350.5), ("6.30", 6.3), ("6,3", 6.3),
     ("12000", 12000), ("R$ 6,00", 6.0), ("", None), ("  ", None), (None, None),
     ("1.234.567", 1234567)],
)
def test_ler_numero(texto, esperado):
    assert ler_numero(texto) == esperado


def test_ler_numero_invalido():
    with pytest.raises(ValueError):
        ler_numero("abc")


def test_formatos():
    assert kg(5000) == "5.000"
    assert kg(1350.5) == "1.350,5"
    assert medida(0.75) == "0,75"
    assert medida(1200) == "1200"
    assert dinheiro(1350) == "R$ 1.350,00"
    assert dinheiro(6.3) == "R$ 6,30"


def test_ler_data():
    assert ler_data("18/11/2026") == datetime.date(2026, 11, 18)
    assert ler_data("18/11/26") == datetime.date(2026, 11, 18)
    assert ler_data("18/11").month == 11
    assert ler_data("") is None
    with pytest.raises(ValueError):
        ler_data("31/02/2026")


def test_chave_ignora_acento_e_maiuscula():
    assert chave("Aço  Forte") == chave("ACO FORTE")
