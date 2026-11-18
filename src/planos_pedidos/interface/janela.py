"""Janela principal: cabeçalho e as 3 abas (Agenda, Pedidos, Planos de corte)."""

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from planos_pedidos import __version__
from planos_pedidos.interface import preferencias
from planos_pedidos.interface.estilo import TEMAS, folha_de_estilo
from planos_pedidos.interface.icones import icone
from planos_pedidos.regras.vendedor import vendedor_atual

TITULO = "PLANOS E PEDIDOS"  # provisório: o nome definido ainda não foi escolhido

ABAS = [  # (texto, ícone) — ícones aprovados por foto
    ("Agenda", "calendar_month"),
    ("Pedidos", "receipt_long"),
    ("Planos de corte", "content_cut"),
]


class JanelaPrincipal(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{TITULO.title()} {__version__}")
        self.tema = preferencias.ler_tema()
        self.vendedor = vendedor_atual()

        central = QWidget(objectName="central")
        self.setCentralWidget(central)
        geral = QVBoxLayout(central)
        geral.setContentsMargins(18, 12, 18, 18)

        topo = QHBoxLayout()
        self.botao_tema = QToolButton(objectName="botao_tema")
        self.botao_tema.setIconSize(QSize(22, 22))
        self.botao_tema.setCursor(Qt.PointingHandCursor)
        self.botao_tema.clicked.connect(self.trocar_tema)
        titulo = QLabel(TITULO, objectName="titulo")
        canto = QLabel(f"{self.vendedor}   ·   v{__version__}", objectName="canto")
        canto.setToolTip("Quem está usando (nome do usuário do Windows) e a versão do programa")
        topo.addWidget(self.botao_tema)
        topo.addStretch()
        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(canto)
        geral.addLayout(topo)

        self.abas = QTabWidget()
        self.abas.setIconSize(QSize(22, 22))
        for texto, _ in ABAS:
            pagina = QWidget()
            aviso = QLabel(f"{texto}: em construção", objectName="dica")
            aviso.setAlignment(Qt.AlignCenter)
            QVBoxLayout(pagina).addWidget(aviso)
            self.abas.addTab(pagina, texto)
        geral.addWidget(self.abas)

        self.aplicar_tema()

    def aplicar_tema(self) -> None:
        """Pinta a janela e os ícones com as cores do tema atual."""
        cores = TEMAS[self.tema]
        self.setStyleSheet(folha_de_estilo(self.tema))
        for i, (_, nome) in enumerate(ABAS):
            self.abas.setTabIcon(i, icone(nome, cores["destaque"]))
        # O botão mostra para onde vai: no escuro, o sol (ir para o claro), e vice-versa.
        vai_para = "claro" if self.tema == "escuro" else "escuro"
        self.botao_tema.setIcon(icone("light_mode" if vai_para == "claro" else "dark_mode",
                                      cores["texto"]))
        self.botao_tema.setToolTip(f"Mudar para modo {vai_para}")

    def trocar_tema(self) -> None:
        self.tema = "claro" if self.tema == "escuro" else "escuro"
        preferencias.gravar_tema(self.tema)
        self.aplicar_tema()
