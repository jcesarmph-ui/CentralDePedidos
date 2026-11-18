"""Números, dinheiro, datas e nomes no jeito brasileiro (vírgula decimal, ponto no milhar)."""

import datetime
import unicodedata


def chave(texto: str) -> str:
    """O que decide se dois nomes são o mesmo: sem espaços repetidos, maiúsculas nem acentos
    ("Superaço" = "SUPERACO")."""
    sem_acento = unicodedata.normalize("NFD", " ".join(texto.split()).casefold())
    return "".join(c for c in sem_acento if not unicodedata.combining(c))


def ler_numero(texto: str | None) -> float | None:
    """Lê "1.500", "0,75", "1.350,50" ou "6.30". Vazio vira None; texto inválido dá ValueError.

    Regra do ponto: com vírgula junto, o ponto é de milhar ("1.350,50"); sozinho e seguido de
    exatamente 3 dígitos também é milhar ("5.000" kg); senão é decimal ("6.30").
    """
    if texto is None:
        return None
    t = texto.strip().replace(" ", "").removeprefix("R$")
    if not t:
        return None
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif t.count(".") >= 1 and all(len(p) == 3 for p in t.split(".")[1:]):
        t = t.replace(".", "")
    return float(t)


def _milhar(texto: str) -> str:
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def kg(valor: float | None) -> str:
    """Quilos sem casas quando é inteiro ("5.000"), senão com uma ("1.350,5")."""
    if valor is None:
        return ""
    if float(valor).is_integer():
        return _milhar(f"{valor:,.0f}")
    return _milhar(f"{valor:,.1f}")


def medida(valor: float | None) -> str:
    """Medida em mm, sem zeros sobrando: 0,75 · 1,5 · 1200."""
    if valor is None:
        return ""
    texto = f"{valor:.3f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def dinheiro(valor: float | None) -> str:
    """R$ com centavos e ponto no milhar (R$ 1.350,00)."""
    if valor is None:
        return ""
    return "R$ " + _milhar(f"{valor:,.2f}")


def data_tela(data: datetime.date | None) -> str:
    return data.strftime("%d/%m/%Y") if data else ""


def ler_data(texto: str | None) -> datetime.date | None:
    """Lê "18/11/2026" (também "18/11/26" e "18/11", que assume o ano atual). Vazio = None."""
    if texto is None or not texto.strip():
        return None
    partes = texto.strip().replace("-", "/").replace(".", "/").split("/")
    if len(partes) == 2:
        partes.append(str(datetime.date.today().year))
    if len(partes) != 3:
        raise ValueError(texto)
    dia, mes, ano = (int(p) for p in partes)
    if ano < 100:
        ano += 2000
    return datetime.date(ano, mes, dia)
