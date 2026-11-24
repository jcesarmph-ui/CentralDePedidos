"""Pedido de cliente: cabeçalho (data, cliente, nº) e vários itens, cada um com seu prazo.

Pedido = material de aço (rolo ou chapa) já cortado, em estoque. Cada item é entregue em até
duas vezes (1ª e 2ª entrega, em kg); a falta é calculada sozinha.
"""

import datetime
from dataclasses import dataclass, field
from enum import StrEnum

from planos_pedidos.regras.formatos import medida


class Tipo(StrEnum):
    ROLO = "Rolo"
    CHAPA = "Chapa"


@dataclass
class Item:
    codigo: str = ""
    tipo: Tipo = Tipo.ROLO
    espessura: float | None = None  # mm
    largura: float | None = None  # mm
    comprimento: float | None = None  # mm — só chapa
    quantidade: float | None = None  # kg
    estoque: float | None = None  # kg que já tem em estoque (a vendedora preenche)
    prazo: datetime.date | None = None
    entrega1: float | None = None  # kg
    entrega2: float | None = None  # kg
    preco_kg: float | None = None  # R$
    observacoes: str = ""
    id: int | None = None


@dataclass
class Pedido:
    data: datetime.date | None = None
    cliente: str = ""
    numero: str = ""
    vendedor: str = ""
    itens: list[Item] = field(default_factory=list)
    atendido: bool = False  # marcado à mão pela vendedora (ex.: cliente desistiu do resto)
    id: int | None = None


def entregue_kg(item: Item) -> float:
    return (item.entrega1 or 0) + (item.entrega2 or 0)


def falta(item: Item) -> float | None:
    """Quanto falta entregar (kg). Negativo = entregou a mais. Sem quantidade: None."""
    if item.quantidade is None:
        return None
    return item.quantidade - entregue_kg(item)


def item_entregue(item: Item) -> bool:
    """Entregue = houve entrega e a falta zerou (ou passou)."""
    f = falta(item)
    return f is not None and entregue_kg(item) > 0 and f <= 0


def tudo_entregue(pedido: Pedido) -> bool:
    """Todos os itens entregues (falta zerada em todos)."""
    return bool(pedido.itens) and all(item_entregue(i) for i in pedido.itens)


def pedido_atendido(pedido: Pedido) -> bool:
    """Atendido = marcado à mão ou tudo entregue (aí vira atendido sozinho)."""
    return pedido.atendido or tudo_entregue(pedido)


def situacao_tela(atendido: bool) -> str:
    return "Atendido" if atendido else "Em aberto"


def descricao(item: Item) -> str:
    """Como na planilha: "ROLO 0,75 x 653" / "CHAPA 1,5 x 1200 x 3000"."""
    medidas = [item.espessura, item.largura]
    if item.tipo == Tipo.CHAPA:
        medidas.append(item.comprimento)
    texto = " x ".join(medida(m) for m in medidas if m is not None)
    return f"{item.tipo.upper()} {texto}".strip()


def problemas_do_item(item: Item) -> list[str]:
    """O que falta preencher no item (vazio = está bom)."""
    faltando = []
    if item.espessura is None:
        faltando.append("espessura")
    if item.largura is None:
        faltando.append("largura")
    if item.tipo == Tipo.CHAPA and item.comprimento is None:
        faltando.append("comprimento")
    if item.quantidade is None:
        faltando.append("quantidade")
    if item.prazo is None:
        faltando.append("prazo de entrega")
    return faltando


def problemas_do_pedido(pedido: Pedido) -> list[str]:
    """Frases para a área de avisos em vermelho. Vazio = pode salvar."""
    avisos = []
    if pedido.data is None:
        avisos.append("Falta a data do pedido.")
    if not pedido.cliente.strip():
        avisos.append("Falta o cliente.")
    if not pedido.numero.strip():
        avisos.append("Falta o número do pedido.")
    if not pedido.itens:
        avisos.append("O pedido precisa de pelo menos um item.")
    for n, item in enumerate(pedido.itens, start=1):
        faltando = problemas_do_item(item)
        if faltando:
            avisos.append(f"Item {n}: falta {', '.join(faltando)}.")
    return avisos


def prazo_mais_proximo(pedido: Pedido) -> datetime.date | None:
    """O prazo do item ainda não entregue que vence primeiro."""
    if pedido_atendido(pedido):
        return None
    prazos = [i.prazo for i in pedido.itens if i.prazo and not item_entregue(i)]
    return min(prazos) if prazos else None


def falta_total(pedido: Pedido) -> float:
    return sum(max(falta(i) or 0, 0) for i in pedido.itens)
