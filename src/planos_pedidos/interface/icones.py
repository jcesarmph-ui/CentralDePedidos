"""Ícones Material Symbols (licença em `icones/LICENSE`), pintados na cor do tema."""

import re
from pathlib import Path

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

PASTA = Path(__file__).parent / "icones"


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
