import datetime

from planos_pedidos.regras.agenda import (
    Situacao,
    Tipo,
    atrasados,
    montar_eventos,
    proximos,
    semanas_do_mes,
)
from planos_pedidos.regras.pedidos import Item, Pedido
from planos_pedidos.regras.planos import Plano

HOJE = datetime.date(2026, 11, 18)  # quarta-feira


def d(n):
    return HOJE + datetime.timedelta(days=n)


def _pedido():
    return Pedido(data=d(-10), cliente="Alfa Chapas", numero="1001", vendedor="JOAO", id=1,
                  itens=[
                      Item(codigo="A", quantidade=100, entrega1=40, prazo=d(-2)),
                      Item(codigo="B", quantidade=50, prazo=d(-2)),
                      Item(codigo="C", quantidade=70, entrega1=70, prazo=d(3)),
                      Item(codigo="D", quantidade=30, prazo=d(1)),
                  ])


def test_pedido_vira_uma_etiqueta_por_prazo():
    eventos = montar_eventos([_pedido()], [], HOJE)
    assert [(e.data, e.situacao) for e in eventos] == [
        (d(-2), Situacao.ATRASADO), (d(1), Situacao.PERTO), (d(3), Situacao.ENTREGUE)]
    assert eventos[0].kg == 110  # 60 + 50 faltando nos dois itens atrasados
    assert eventos[0].titulo == "1001" and eventos[0].tipo == Tipo.PEDIDO


def test_plano_sem_status_com_data_passada_nao_fica_atrasado():
    planos = [Plano(cliente="Beta Metais", lote="L1", quantidade="2.000", entrega=d(-1), id=7),
              Plano(cliente="Beta Metais", lote="L2", quantidade="saldo total", entrega=d(0),
                    id=8, critico=True)]
    eventos = montar_eventos([], planos, HOJE)
    assert [e.situacao for e in eventos] == [Situacao.PASSOU, Situacao.PERTO]
    assert eventos[0].kg == 2000 and eventos[1].kg == 0
    assert eventos[1].critico


def test_atrasados_e_proximos():
    eventos = montar_eventos([_pedido()], [Plano(lote="L", entrega=d(5), id=3)], HOJE)
    assert [e.data for e in atrasados(eventos)] == [d(-2)]
    assert [e.data for e in proximos(eventos, HOJE)] == [d(1), d(5)]  # sem o entregue


def test_criticos_primeiro_no_dia():
    planos = [Plano(lote="normal", entrega=d(4), id=1),
              Plano(lote="urgente", entrega=d(4), id=2, critico=True)]
    assert [e.titulo for e in montar_eventos([], planos, HOJE)] == ["urgente", "normal"]


def test_semanas_do_mes_comecam_na_segunda():
    semanas = semanas_do_mes(2026, 11)
    assert len(semanas) == 6 and all(len(s) == 7 for s in semanas)
    assert semanas[0][0] == datetime.date(2026, 10, 26)  # segunda antes do dia 1º (domingo)
    assert semanas[0][6] == datetime.date(2026, 11, 1)
