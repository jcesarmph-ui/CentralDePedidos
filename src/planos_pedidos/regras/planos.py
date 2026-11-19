"""Plano de corte: o serviço de cortar uma bobina (a "bobina mãe") para um cliente.

Descrição do item e bobina mãe são texto livre, copiados do sistema da empresa. A quantidade
quase sempre é em kg, mas a planilha também tem "1 un" e "saldo total": por isso é texto, e
quando é número aparece formatado em kg.
"""

import datetime
from dataclasses import dataclass

from planos_pedidos.regras.formatos import data_tela, kg, ler_numero


@dataclass
class Plano:
    data: datetime.date | None = None
    cliente: str = ""
    item: str = ""
    lote: str = ""
    descricao: str = ""
    bobina_mae: str = ""
    quantidade: str = ""  # "2000", "1 un", "saldo total"…
    entrega: datetime.date | None = None
    observacoes: str = ""
    critico: bool = False  # entrega crítica (na planilha: "12/08/2026 - CRITICO")
    vendedor: str = ""
    id: int | None = None


def quantidade_kg(texto: str) -> float | None:
    """O número em kg, se a quantidade for número ("2.000", "2000 kg"); senão None."""
    t = texto.strip().lower().removesuffix("kg").strip()
    try:
        return ler_numero(t)
    except ValueError:
        return None


def quantidade_tela(texto: str) -> str:
    """"2000" → "2.000 kg"; "1 un" e "saldo total" ficam como foram escritos."""
    valor = quantidade_kg(texto)
    return f"{kg(valor)} kg" if valor is not None else texto.strip()


def problemas_do_plano(plano: Plano) -> list[str]:
    avisos = []
    if plano.data is None:
        avisos.append("Falta a data do plano.")
    if not plano.cliente.strip():
        avisos.append("Falta o cliente.")
    if not plano.descricao.strip():
        avisos.append("Falta a descrição do item.")
    if not plano.quantidade.strip():
        avisos.append("Falta a quantidade.")
    if plano.entrega is None:
        avisos.append("Falta a data de entrega.")
    return avisos


def entrega_tela(plano: Plano) -> str:
    """"19/11/2026" ou "19/11/2026 - CRÍTICO"."""
    texto = data_tela(plano.entrega)
    return f"{texto} - CRÍTICO" if plano.critico and texto else texto
