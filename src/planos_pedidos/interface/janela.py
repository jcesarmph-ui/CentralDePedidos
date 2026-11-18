"""Janela principal: cabeçalho e as 3 abas (Agenda, Pedidos, Planos de corte)."""

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from planos_pedidos import __version__
from planos_pedidos.dados.repositorio import Repositorio
from planos_pedidos.interface import preferencias
from planos_pedidos.interface.aba_pedidos import AbaPedidos
from planos_pedidos.interface.componentes import instalar_filtro_roda
from planos_pedidos.interface.estilo import CORES, aplicar_tema
from planos_pedidos.interface.icones import icone, repintar
from planos_pedidos.regras.vendedor import vendedor_atual

TITULO = "PLANOS E PEDIDOS"  # provisório: o nome definido ainda não foi escolhido

ABAS = [  # (texto, ícone) — ícones aprovados por foto
    ("Agenda", "calendar_month"),
    ("Pedidos", "receipt_long"),
    ("Planos de corte", "content_cut"),
]


def _em_construcao(texto: str) -> QWidget:
    pagina = QWidget()
    aviso = QLabel(f"{texto}: em construção", objectName="dica")
    aviso.setAlignment(Qt.AlignCenter)
    QVBoxLayout(pagina).addWidget(aviso)
    return pagina


class JanelaPrincipal(QMainWindow):
    def __init__(self, repo: Repositorio) -> None:
        super().__init__()
        instalar_filtro_roda()
        self.setWindowTitle(f"{TITULO.title()} {__version__}")
        self.repo = repo
        self.tema = preferencias.ler_tema()
        self.vendedor = vendedor_atual()
        # No programa inteiro (não só nesta janela): a janela do pedido abre separada.
        QApplication.instance().setStyleSheet(aplicar_tema(self.tema))  # antes de montar

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
        self.aba_pedidos = AbaPedidos(repo, self.vendedor)
        self.abas.addTab(_em_construcao("Agenda"), ABAS[0][0])
        self.abas.addTab(self.aba_pedidos, ABAS[1][0])
        self.abas.addTab(_em_construcao("Planos de corte"), ABAS[2][0])
        geral.addWidget(self.abas)

        self.pintar_icones()

    def pintar_icones(self) -> None:
        for i, (_, nome) in enumerate(ABAS):
            self.abas.setTabIcon(i, icone(nome, CORES["destaque"]))
        # O botão mostra para onde vai: no escuro, o sol (ir para o claro), e vice-versa.
        vai_para = "claro" if self.tema == "escuro" else "escuro"
        self.botao_tema.setIcon(icone("light_mode" if vai_para == "claro" else "dark_mode",
                                      CORES["texto"]))
        self.botao_tema.setToolTip(f"Mudar para modo {vai_para}")

    def trocar_tema(self) -> None:
        """Troca na hora, sem fechar: estilo, ícones e cores da tabela."""
        self.tema = "claro" if self.tema == "escuro" else "escuro"
        preferencias.gravar_tema(self.tema)
        QApplication.instance().setStyleSheet(aplicar_tema(self.tema))
        repintar(CORES)
        self.pintar_icones()
        self.aba_pedidos.preencher()
