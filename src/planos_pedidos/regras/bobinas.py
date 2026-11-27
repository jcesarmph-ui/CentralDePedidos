"""Estoque de bobinas exportado do ERP para Excel (relatório de estoque).

Regras combinadas com o usuário (2026-11-27):
- as colunas são achadas **pelo nome** (sem ligar para maiúsculas, acentos e espaços), assim a
  ordem pode mudar no ERP sem quebrar a importação;
- só entram linhas com **Ori. = LOT** (as de ORD ficam de fora);
- quanto dá para planejar = coluna **Disponibilidade** (valor do ERP, sem fazer conta);
- bobina com Disponibilidade 0 (ou menos) **não aparece** para escolher;
- preço, ICMS, IPI e fornecedor **não entram** no programa.
"""

import datetime
from dataclasses import dataclass
from pathlib import Path

from planos_pedidos.regras.formatos import chave


class PlanilhaInvalida(ValueError):
    """A planilha não tem o formato esperado (ex.: falta uma coluna obrigatória)."""


@dataclass
class Bobina:
    lote: str
    codigo: str  # Cód.Ref. (20-01-xxx, SB-001…)
    espessura: float | None
    largura: float | None
    comprimento: float | None  # 0/None = bobina; com valor = chapa/blank
    disponivel: float  # kg que dá para planejar
    saldo: float | None
    liberado: bool  # Liber./Util. = "S"
    emissao: datetime.date | None = None
    acabamento: str = ""
    classificacao: str = ""  # norma
    local: str = ""  # posição no pátio


# nome no programa -> nome da coluna no ERP (comparado com chave(); o ERP escreve
# "Disponíbilidade" com acento errado, e chave() tira o acento, então bate igual)
_COLUNAS = {
    "origem": "Ori.",
    "emissao": "Dt. Emissão",
    "lote": "Núm. Lote",
    "liberado": "Liber./Util.",
    "codigo": "Cód.Ref.",
    "espessura": "Espessura (mm)",
    "largura": "Largura (mm)",
    "comprimento": "Compr./B.Maior (mm)",
    "disponivel": "Disponibilidade",
    "saldo": "Saldo (R)",
    "acabamento": "Acabamento de Superfície",
    "classificacao": "Classificação",
    "local": "Local",
}
_OBRIGATORIAS = ("origem", "lote", "codigo", "disponivel")


def _chave_coluna(texto: object) -> str:
    return "".join(chave(str(texto or "")).split())


def _texto(valor: object) -> str:
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)  # lote numérico 12345.0 -> "12345"
    return str(valor).strip()


def _numero(valor: object) -> float | None:
    if valor is None or valor == "":
        return None
    if isinstance(valor, int | float):
        return float(valor)
    try:
        return float(str(valor).strip().replace(".", "").replace(",", "."))
    except ValueError:
        return None


def _data(valor: object) -> datetime.date | None:
    if isinstance(valor, datetime.datetime):
        return valor.date()
    if isinstance(valor, datetime.date):
        return valor
    return None


def ler_linhas(linhas: list[tuple]) -> list[Bobina]:
    """Transforma as linhas da planilha (a 1ª é o cabeçalho) nas bobinas que dá para usar."""
    if not linhas:
        raise PlanilhaInvalida("A planilha está vazia.")
    posicao = {_chave_coluna(nome): i for i, nome in enumerate(linhas[0])}
    indice = {}
    for campo, nome in _COLUNAS.items():
        i = posicao.get(_chave_coluna(nome))
        if i is None and campo in _OBRIGATORIAS:
            raise PlanilhaInvalida(f'Falta a coluna "{nome}" na planilha.')
        indice[campo] = i

    def valor(linha: tuple, campo: str) -> object:
        i = indice[campo]
        return linha[i] if i is not None and i < len(linha) else None

    bobinas = []
    for linha in linhas[1:]:
        if _texto(valor(linha, "origem")).upper() != "LOT":
            continue
        disponivel = _numero(valor(linha, "disponivel"))
        if not disponivel or disponivel <= 0:
            continue
        comprimento = _numero(valor(linha, "comprimento"))
        bobinas.append(
            Bobina(
                lote=_texto(valor(linha, "lote")),
                codigo=_texto(valor(linha, "codigo")),
                espessura=_numero(valor(linha, "espessura")),
                largura=_numero(valor(linha, "largura")),
                comprimento=comprimento or None,
                disponivel=disponivel,
                saldo=_numero(valor(linha, "saldo")),
                liberado=_texto(valor(linha, "liberado")).upper() == "S",
                emissao=_data(valor(linha, "emissao")),
                acabamento=_texto(valor(linha, "acabamento")),
                classificacao=_texto(valor(linha, "classificacao")),
                local=_texto(valor(linha, "local")),
            )
        )
    return bobinas


def importar_planilha(caminho: str | Path) -> list[Bobina]:
    """Lê o .xlsx exportado do ERP (primeira aba, cabeçalho na linha 1)."""
    import openpyxl  # só carrega quando importa, para o programa abrir rápido

    try:
        livro = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
    except Exception as erro:  # arquivo aberto, corrompido, não é Excel…
        raise PlanilhaInvalida(f"Não foi possível abrir a planilha: {erro}") from erro
    try:
        linhas = list(livro.worksheets[0].iter_rows(values_only=True))
    finally:
        livro.close()
    return ler_linhas(linhas)
