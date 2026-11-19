"""Lixeira, trava por pedido/plano e filtro por vendedora (dados fictícios)."""

import datetime
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from planos_pedidos.dados.repositorio import Repositorio  # noqa: E402
from planos_pedidos.interface.janela import JanelaPrincipal  # noqa: E402
from planos_pedidos.regras.pedidos import Item, Pedido, Tipo  # noqa: E402
from planos_pedidos.regras.planos import Plano  # noqa: E402
from planos_pedidos.regras.vendedor import filtrar_por_vendedor  # noqa: E402

HOJE = datetime.date(2026, 11, 19)


@pytest.fixture
def repo(tmp_path):
    return Repositorio(tmp_path / "teste.db")


def _pedido(repo, vendedor="ANA", numero="1001"):
    p = Pedido(data=HOJE, cliente="Alfa Chapas", numero=numero, vendedor=vendedor,
               itens=[Item(tipo=Tipo.ROLO, espessura=1, largura=100, quantidade=500,
                           prazo=HOJE)])
    return repo.salvar_pedido(p)


def _plano(repo, vendedor="CARLOS"):
    return repo.salvar_plano(Plano(data=HOJE, cliente="Beta Aços", descricao="BOBINA 2,00",
                                   quantidade="1.000", entrega=HOJE, vendedor=vendedor))


def test_excluir_vai_para_lixeira_e_restaura(repo):
    pid, lid = _pedido(repo), _plano(repo)
    repo.excluir("pedido", pid, quem="CARLOS")
    repo.excluir("plano", lid, quem="CARLOS")
    assert repo.pedidos() == [] and repo.planos() == []
    lixo = repo.lixeira()
    assert {t for t, *_ in lixo} == {"pedido", "plano"}
    assert all(quem == "CARLOS" for *_, quem in lixo)
    repo.restaurar("pedido", pid)
    assert [p.id for p in repo.pedidos()] == [pid]
    assert [t for t, *_ in repo.lixeira()] == ["plano"]


def test_excluir_de_vez_so_apaga_o_que_esta_na_lixeira(repo):
    pid = _pedido(repo)
    repo.excluir_de_vez("pedido", pid)  # ainda ativo: não apaga
    assert repo.pedido(pid) is not None
    repo.excluir("pedido", pid)
    repo.excluir_de_vez("pedido", pid)
    assert repo.pedido(pid) is None and repo.lixeira() == []


def test_trava_bloqueia_outra_pessoa(repo):
    pid = _pedido(repo)
    assert repo.pegar_trava("pedido", pid, "ANA", "PC1") is None
    assert repo.pegar_trava("pedido", pid, "CARLOS", "PC2") == ("ANA", "PC1")
    # mesma pessoa no mesmo PC entra de novo; outro registro está livre
    assert repo.pegar_trava("pedido", pid, "ANA", "PC1") is None
    assert repo.pegar_trava("plano", pid, "CARLOS", "PC2") is None
    repo.soltar_trava("pedido", pid, "ANA", "PC1")
    assert repo.pegar_trava("pedido", pid, "CARLOS", "PC2") is None


def test_trava_solta_sozinha_apos_2_min_sem_sinal(repo):
    pid = _pedido(repo)
    antes = datetime.datetime.now() - datetime.timedelta(minutes=3)
    repo.pegar_trava("pedido", pid, "ANA", "PC1", agora=antes)
    assert repo.pegar_trava("pedido", pid, "CARLOS", "PC2") is None


def test_filtro_por_vendedor(repo):
    _pedido(repo, "ANA", "1")
    _pedido(repo, "CARLOS", "2")
    pedidos = repo.pedidos()
    assert [p.numero for p in filtrar_por_vendedor(pedidos, "CARLOS")] == ["2"]
    assert len(filtrar_por_vendedor(pedidos, "")) == 2


def test_tela_filtra_e_avisa_trava(repo, tmp_path):
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    _ = QApplication.instance() or QApplication([])
    pid = _pedido(repo, "ANA", "1")
    _pedido(repo, "CARLOS", "2")
    _plano(repo, "CARLOS")
    j = JanelaPrincipal(repo)
    j.filtro.setCurrentText("ANA")
    assert j.aba_pedidos.tabela.rowCount() == 1
    assert j.aba_planos.tabela.rowCount() == 0
    j.filtro.setCurrentText("Todos")
    assert j.aba_pedidos.tabela.rowCount() == 2
    # outra pessoa está editando: não abre e mostra o aviso amarelo com o nome
    repo.pegar_trava("pedido", pid, "OUTRA", "PC9")
    j.aba_pedidos.abrir_id(pid)
    assert "OUTRA está mexendo" in j.aviso.text() and not j.aviso.isHidden()
    # excluir pela tela aparece na Lixeira
    repo.excluir("pedido", pid)
    j.aba_pedidos.mudou.emit()
    assert j.aba_lixeira.tabela.rowCount() == 1
    j.close()
