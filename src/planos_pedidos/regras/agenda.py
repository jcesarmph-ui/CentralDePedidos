"""Agenda: o que vence em cada dia (pedidos e planos de corte).

Cada pedido vira uma etiqueta por prazo (itens do mesmo pedido com o mesmo prazo ficam juntos);
cada plano vira uma etiqueta na data de entrega.

Situação (cor da etiqueta):
- ATRASADO: prazo vencido e ainda em aberto;
- PERTO: vence hoje ou amanhã (pedido faltando entregar ou plano);
- NO_PRAZO: vence depois de amanhã;
- ENTREGUE: pedido/plano marcado "Atendido" (o pedido também quando tudo foi entregue)
  ou itens daquele prazo do pedido já entregues.
"""

import datetime
from dataclasses import dataclass
from enum import StrEnum

from planos_pedidos.regras.pedidos import (
    Pedido,
    descricao,
    falta,
    item_entregue,
    pedido_atendido,
)
from planos_pedidos.regras.planos import Plano, quantidade_kg


class Situacao(StrEnum):
    ATRASADO = "atrasado"
    PERTO = "hoje/amanhã"
    NO_PRAZO = "no prazo"
    ENTREGUE = "entregue"


class Tipo(StrEnum):
    PEDIDO = "pedido"
    PLANO = "plano"


@dataclass
class Evento:
    data: datetime.date
    tipo: Tipo
    id: int
    titulo: str  # nº do pedido ou lote do plano
    cliente: str
    kg: float  # quanto falta (pedido) ou a quantidade (plano, se for número)
    situacao: Situacao
    detalhe: str  # descrição curta para a dica do mouse
    vendedor: str = ""
    critico: bool = False


def _situacao_por_data(data: datetime.date, hoje: datetime.date) -> Situacao:
    if data < hoje:
        return Situacao.ATRASADO
    if data <= hoje + datetime.timedelta(days=1):
        return Situacao.PERTO
    return Situacao.NO_PRAZO


def eventos_do_pedido(pedido: Pedido, hoje: datetime.date) -> list[Evento]:
    por_prazo: dict[datetime.date, list] = {}
    for item in pedido.itens:
        if item.prazo:
            por_prazo.setdefault(item.prazo, []).append(item)
    atendido = pedido_atendido(pedido)
    eventos = []
    for prazo, itens in sorted(por_prazo.items()):
        entregue = atendido or all(item_entregue(i) for i in itens)
        situacao = Situacao.ENTREGUE if entregue else _situacao_por_data(prazo, hoje)
        faltando = sum(max(falta(i) or 0, 0) for i in itens)
        eventos.append(Evento(
            data=prazo, tipo=Tipo.PEDIDO, id=pedido.id, titulo=pedido.numero,
            cliente=pedido.cliente, kg=faltando, situacao=situacao,
            detalhe="\n".join(f"{i.codigo}  {descricao(i)}".strip() for i in itens),
            vendedor=pedido.vendedor))
    return eventos


def evento_do_plano(plano: Plano, hoje: datetime.date) -> Evento | None:
    if plano.entrega is None:
        return None
    situacao = (Situacao.ENTREGUE if plano.atendido
                else _situacao_por_data(plano.entrega, hoje))
    return Evento(
        data=plano.entrega, tipo=Tipo.PLANO, id=plano.id, titulo=plano.lote or plano.item,
        cliente=plano.cliente, kg=quantidade_kg(plano.quantidade) or 0, situacao=situacao,
        detalhe=f"{plano.descricao}\n{plano.bobina_mae}".strip(), vendedor=plano.vendedor,
        critico=plano.critico)


def montar_eventos(pedidos: list[Pedido], planos: list[Plano],
                   hoje: datetime.date | None = None) -> list[Evento]:
    hoje = hoje or datetime.date.today()
    eventos = [e for p in pedidos for e in eventos_do_pedido(p, hoje)]
    eventos += [e for p in planos if (e := evento_do_plano(p, hoje))]
    # No dia: atrasados e críticos primeiro.
    ordem = {Situacao.ATRASADO: 0, Situacao.PERTO: 1, Situacao.NO_PRAZO: 2,
             Situacao.ENTREGUE: 3}
    return sorted(eventos, key=lambda e: (e.data, not e.critico, ordem[e.situacao]))


def atrasados(eventos: list[Evento]) -> list[Evento]:
    return [e for e in eventos if e.situacao == Situacao.ATRASADO]


def proximos(eventos: list[Evento], hoje: datetime.date, dias: int = 7) -> list[Evento]:
    """O que vence de hoje até `dias` dias à frente (sem os já entregues)."""
    fim = hoje + datetime.timedelta(days=dias)
    return [e for e in eventos
            if hoje <= e.data <= fim and e.situacao != Situacao.ENTREGUE]


def semanas_do_mes(ano: int, mes: int) -> list[list[datetime.date]]:
    """As semanas (segunda a domingo) que aparecem no calendário do mês, sempre 6 linhas."""
    primeiro = datetime.date(ano, mes, 1)
    inicio = primeiro - datetime.timedelta(days=primeiro.weekday())
    return [[inicio + datetime.timedelta(days=7 * s + d) for d in range(7)] for s in range(6)]
