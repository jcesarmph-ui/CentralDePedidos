"""Ícones Material Symbols (licença em `icones/LICENSE`), pintados na cor do tema.

`por_icone` lembra onde cada ícone foi posto e com qual papel de cor ("texto", "destaque"…);
na troca de tema, `repintar` pinta todos de novo com as cores do tema novo.
"""

import re
import weakref
from pathlib import Path

import shiboken6
from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

PASTA = Path(__file__).parent / "icones"

_POSTOS: list[tuple[weakref.ref, str, str]] = []


def svg_colorido(nome: str, cor: str) -> str:
    """O SVG `nome` (sem .svg) com tudo pintado de `cor`."""
    texto = (PASTA / f"{nome}.svg").read_text(encoding="utf-8")
    return re.sub(r"<path ", f'<path fill="{cor}" ', texto)


def pixmap(nome: str, cor: str, tamanho: int = 48) -> QPixmap:
    renderizador = QSvgRenderer(QByteArray(svg_colorido(nome, cor).encode("utf-8")))
    imagem = QPixmap(tamanho, tamanho)
    imagem.fill(Qt.transparent)
    pintor = QPainter(imagem)
    pintor.setRenderHint(QPainter.Antialiasing)
    renderizador.render(pintor)
    pintor.end()
    return imagem


def icone(nome: str, cor: str) -> QIcon:
    return QIcon(pixmap(nome, cor))


def por_icone(alvo, nome: str, papel: str, cores: dict[str, str], tamanho: int = 22) -> None:
    """Põe o ícone no botão/rótulo na cor do `papel` e lembra para repintar na troca de tema.
    Papel "branco" = sempre branco (botão colorido)."""
    _POSTOS.append((weakref.ref(alvo), nome, papel))
    _pintar(alvo, nome, papel, cores, tamanho)


def _pintar(alvo, nome: str, papel: str, cores: dict[str, str], tamanho: int = 22) -> None:
    cor = "#ffffff" if papel == "branco" else cores.get(papel, papel)
    if hasattr(alvo, "setIcon"):
        alvo.setIcon(icone(nome, cor))
        if hasattr(alvo, "setIconSize"):  # QAction (lupa do campo) não tem
            alvo.setIconSize(QSize(tamanho, tamanho))
    else:  # QLabel
        alvo.setPixmap(pixmap(nome, cor, tamanho))


def repintar(cores: dict[str, str]) -> None:
    vivos = []
    for ref, nome, papel in _POSTOS:
        alvo = ref()
        if alvo is not None and shiboken6.isValid(alvo):
            _pintar(alvo, nome, papel, cores)
            vivos.append((ref, nome, papel))
    _POSTOS[:] = vivos
