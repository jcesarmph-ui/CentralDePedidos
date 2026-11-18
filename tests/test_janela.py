"""Janela e tela de pedidos, sem mostrar na tela (nomes fictícios)."""

import datetime
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from planos_pedidos.dados.repositorio import Repositorio  # noqa: E402
from planos_pedidos.interface.aba_pedidos import JanelaPedido, cores_do_prazo  # noqa: E402
from planos_pedidos.interface.estilo import ATRASADO, ENTREGUE, HOJE  # noqa: E402
from planos_pedidos.interface.janela import JanelaPrincipal  # noqa: E402


@pytest.fixture
def repo(tmp_path):
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    _ = QApplication.instance() or QApplication([])
    r = Repositorio(tmp_path / "teste.db")
    r.adicionar_cliente("Alfa Chapas")
    return r


@pytest.fixture
def janela(repo):
    j = JanelaPrincipal(repo)
    yield j
    j.close()


def test_tres_abas(janela):
    nomes = [janela.abas.tabText(i) for i in range(janela.abas.count())]
    assert nomes == ["Agenda", "Pedidos", "Planos de corte"]


def test_troca_de_tema_e_lembrada(janela, repo):
    assert janela.tema == "escuro"
    janela.trocar_tema()
    assert janela.tema == "claro"
    assert JanelaPrincipal(repo).tema == "claro"  # abre de novo já no claro


def _preencher_item(linha, quantidade="5.000", e1="", prazo="20/11/2026"):
    linha.codigo.setText("10-001")
    linha.espessura.setText("0,75")
    linha.largura.setText("653")
    linha.quantidade.setText(quantidade)
    linha.prazo.campo.setText(prazo)
    linha.entrega1.setText(e1)
    linha.preco.setText("6,00")


def test_falta_atualiza_sozinha_e_mostra_check(repo):
    j = JanelaPedido(repo, "JOAO")
    linha = j.linhas[0]
    _preencher_item(linha, quantidade="5.000", e1="4.524")
    assert linha.falta.text() == "476"
    linha.entrega2.setText("476")
    assert linha.falta.text() == "0"
    assert linha.falta.objectName() == "falta_ok"
    assert not linha.falta_icone.isHidden()


def test_rolo_desliga_comprimento(repo):
    linha = JanelaPedido(repo, "JOAO").linhas[0]
    linha.tipo.setCurrentText("Chapa")
    assert linha.comprimento.isEnabled()
    linha.tipo.setCurrentText("Rolo")
    assert not linha.comprimento.isEnabled()


def test_salvar_pedido_com_dois_itens(repo):
    j = JanelaPedido(repo, "JOAO")
    j.cliente.setText("alfa chapas")  # grafia diferente: vira o nome da lista
    j.numero.setText("1001")
    _preencher_item(j.linhas[0])
    j.copiar_ultimo()
    assert j.linhas[1].espessura.text() == "0,75"  # copiou as medidas
    assert j.linhas[1].quantidade.text() == ""  # quantidade não é copiada
    j.linhas[1].codigo.setText("10-002")
    j.linhas[1].quantidade.setText("2.000")
    j.salvar()
    assert j.erros.isHidden()
    salvo = repo.pedidos()[0]
    assert salvo.cliente == "Alfa Chapas" and salvo.vendedor == "JOAO"
    assert [i.quantidade for i in salvo.itens] == [5000, 2000]


def test_campos_faltando_aparecem_em_vermelho_sem_salvar(repo):
    j = JanelaPedido(repo, "JOAO")
    j.linhas[0].espessura.setText("abc")
    j.salvar()
    assert not j.erros.isHidden()
    assert "Falta o cliente." in j.erros.text()
    assert "número inválido em espessura" in j.erros.text()
    assert repo.pedidos() == []


def test_cliente_novo_pede_confirmacao(repo, monkeypatch):
    j = JanelaPedido(repo, "JOAO")
    j.cliente.setText("Gama Aços")
    assert "cliente novo" in j.aviso_cliente.text()
    j.numero.setText("1002")
    _preencher_item(j.linhas[0])
    monkeypatch.setattr(QMessageBox, "exec", lambda self: None)  # "Voltar": não clicou em criar
    j.salvar()
    assert repo.pedidos() == []
    monkeypatch.setattr(j, "_confirmar_cliente_novo", lambda nome: True)
    j.salvar()
    assert "Gama Aços" in repo.clientes()


def test_cores_do_prazo():
    hoje = datetime.date(2026, 11, 18)
    assert cores_do_prazo(hoje - datetime.timedelta(days=1), False, hoje) == ATRASADO
    assert cores_do_prazo(hoje + datetime.timedelta(days=1), False, hoje) == HOJE
    assert cores_do_prazo(hoje + datetime.timedelta(days=5), False, hoje) is None
    assert cores_do_prazo(hoje - datetime.timedelta(days=9), True, hoje) == ENTREGUE
