"""A janela abre com as 3 abas e troca de tema na hora (sem mostrar na tela)."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from planos_pedidos.interface.janela import JanelaPrincipal  # noqa: E402


@pytest.fixture
def janela(tmp_path):
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    _ = QApplication.instance() or QApplication([])
    j = JanelaPrincipal()
    yield j
    j.close()


def test_tres_abas(janela):
    nomes = [janela.abas.tabText(i) for i in range(janela.abas.count())]
    assert nomes == ["Agenda", "Pedidos", "Planos de corte"]


def test_troca_de_tema_e_lembrada(janela):
    assert janela.tema == "escuro"
    janela.trocar_tema()
    assert janela.tema == "claro"
    assert JanelaPrincipal().tema == "claro"  # abre de novo já no claro
