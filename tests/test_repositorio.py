"""Banco: com nomes fictícios, numa pasta temporária."""

import datetime

import pytest

from planos_pedidos.dados.repositorio import Repositorio
from planos_pedidos.regras.pedidos import Item, Pedido, Tipo

HOJE = datetime.date(2026, 11, 18)


@pytest.fixture
def repo(tmp_path):
    return Repositorio(tmp_path / "teste.db")


def test_banco_nao_usa_wal(repo):
    with repo._transacao() as con:
        assert con.execute("PRAGMA journal_mode").fetchone()[0] == "delete"


def test_cliente_repetido_com_outra_grafia_vira_um_so(repo):
    assert repo.adicionar_cliente("Aço  Forte") == "Aço Forte"
    assert repo.adicionar_cliente("ACO FORTE") == "Aço Forte"
    assert repo.clientes() == ["Aço Forte"]


def test_importar_lista_de_clientes(repo, tmp_path):
    lista = tmp_path / "clientes.txt"
    lista.write_text("Beta Metais\nAlfa Chapas\n\nbeta metais\n", encoding="utf-8")
    assert repo.importar_clientes(lista) == 2
    assert repo.clientes() == ["Alfa Chapas", "Beta Metais"]
    assert repo.importar_clientes(tmp_path / "nao_existe.txt") == 0


def _pedido():
    return Pedido(data=HOJE, cliente="Alfa Chapas", numero="1001", vendedor="JOAO", itens=[
        Item(codigo="10-001", tipo=Tipo.ROLO, espessura=0.75, largura=653, comprimento=500,
             quantidade=5000, prazo=HOJE, entrega1=4524, preco_kg=6.0),
        Item(codigo="10-002", tipo=Tipo.CHAPA, espessura=1.5, largura=1200, comprimento=3000,
             quantidade=3000, prazo=HOJE + datetime.timedelta(days=2), observacoes="urgente"),
    ])


def test_salvar_e_ler_pedido_com_itens(repo):
    pid = repo.salvar_pedido(_pedido())
    lido = repo.pedido(pid)
    assert lido.cliente == "Alfa Chapas" and lido.vendedor == "JOAO"
    assert [i.codigo for i in lido.itens] == ["10-001", "10-002"]
    assert lido.itens[0].comprimento is None  # rolo não guarda comprimento
    assert lido.itens[0].entrega1 == 4524
    assert lido.itens[1].observacoes == "urgente"


def test_editar_pedido_regrava_itens(repo):
    pedido = _pedido()
    repo.salvar_pedido(pedido)
    pedido.itens.pop()
    pedido.itens[0].entrega2 = 476
    repo.salvar_pedido(pedido, quem="MARIA")
    lido = repo.pedido(pedido.id)
    assert len(lido.itens) == 1 and lido.itens[0].entrega2 == 476
    assert len(repo.pedidos()) == 1


def test_numero_em_uso(repo):
    pid = repo.salvar_pedido(_pedido())
    assert repo.numero_em_uso("1001")
    assert not repo.numero_em_uso("1001", ignorar_id=pid)
    assert not repo.numero_em_uso("9999")
