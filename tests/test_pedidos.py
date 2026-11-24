import datetime

from planos_pedidos.regras.pedidos import (
    Item,
    Pedido,
    Tipo,
    descricao,
    falta,
    falta_total,
    item_entregue,
    prazo_mais_proximo,
    problemas_do_pedido,
)

HOJE = datetime.date(2026, 11, 18)


def test_falta_calculada_pelas_entregas():
    item = Item(quantidade=2000, entrega1=886, entrega2=783)
    assert falta(item) == 331
    assert not item_entregue(item)


def test_entregue_quando_falta_zera():
    item = Item(quantidade=5060, entrega1=5060)
    assert falta(item) == 0
    assert item_entregue(item)


def test_entregou_a_mais_da_falta_negativa_e_conta_como_entregue():
    item = Item(quantidade=3000, entrega1=1217, entrega2=2768)
    assert falta(item) == -985
    assert item_entregue(item)


def test_sem_entrega_nao_esta_entregue():
    assert not item_entregue(Item(quantidade=0))
    assert falta(Item()) is None


def test_descricao_rolo_sem_comprimento():
    item = Item(tipo=Tipo.ROLO, espessura=0.75, largura=653, comprimento=999)
    assert descricao(item) == "ROLO 0,75 x 653"


def test_descricao_chapa():
    assert descricao(Item(tipo=Tipo.CHAPA, espessura=1.5, largura=1200,
                          comprimento=3000)) == "CHAPA 1,5 x 1200 x 3000"


def test_problemas_do_pedido():
    pedido = Pedido(itens=[Item(tipo=Tipo.CHAPA, espessura=1, largura=1000)])
    avisos = problemas_do_pedido(pedido)
    assert "Falta o cliente." in avisos
    assert "Item 1: falta comprimento, quantidade, prazo de entrega." in avisos
    bom = Pedido(data=HOJE, cliente="Cliente A", numero="100",
                 itens=[Item(espessura=1, largura=100, quantidade=500, prazo=HOJE)])
    assert problemas_do_pedido(bom) == []


def test_prazo_mais_proximo_ignora_entregues():
    pedido = Pedido(itens=[
        Item(quantidade=100, entrega1=100, prazo=HOJE),
        Item(quantidade=100, prazo=HOJE + datetime.timedelta(days=3)),
    ])
    assert prazo_mais_proximo(pedido) == HOJE + datetime.timedelta(days=3)
    assert falta_total(pedido) == 100


def test_pedido_atendido_a_mao_ou_sozinho_quando_tudo_entregue():
    from planos_pedidos.regras.pedidos import pedido_atendido, prazo_mais_proximo

    aberto = Pedido(itens=[Item(quantidade=100, entrega1=40,
                                prazo=datetime.date(2026, 12, 1))])
    assert not pedido_atendido(aberto)
    aberto.atendido = True  # cliente desistiu do resto
    assert pedido_atendido(aberto) and prazo_mais_proximo(aberto) is None
    entregue = Pedido(itens=[Item(quantidade=100, entrega1=60, entrega2=40)])
    assert pedido_atendido(entregue)  # sozinho
    assert not pedido_atendido(Pedido())  # sem itens não conta
