"""Janela principal: cabeçalho e as 3 abas (Agenda, Pedidos, Planos de corte)."""

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from planos_pedidos import __version__
from planos_pedidos.dados.caminhos import LISTA_VENDEDORES, pasta_dados
from planos_pedidos.dados.repositorio import Repositorio
from planos_pedidos.interface import preferencias
from planos_pedidos.interface.aba_agenda import AbaAgenda
from planos_pedidos.interface.aba_lixeira import AbaLixeira
from planos_pedidos.interface.aba_pedidos import AbaPedidos
from planos_pedidos.interface.aba_planos import AbaPlanos
from planos_pedidos.interface.componentes import RotuloAviso, instalar_filtro_roda
from planos_pedidos.interface.estilo import CORES, aplicar_tema
from planos_pedidos.interface.icones import icone, repintar
from planos_pedidos.regras.vendedor import ler_vendedores, vendedor_atual

TITULO = "CENTRAL DE PEDIDOS"

ABAS = [  # (texto, ícone) — ícones aprovados por foto
    ("Agenda", "calendar_month"),
    ("Pedidos", "receipt_long"),
    ("Planos de corte", "content_cut"),
    ("Lixeira", "delete"),
]
TODOS = "Todos"


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
        # Filtro "Registrado por": vale para todas as abas de uma vez.
        self.rotulo_filtro = QLabel(objectName="rotulo_filtro")
        self.filtro = QComboBox()
        self.filtro.addItems([TODOS, *ler_vendedores(pasta_dados() / LISTA_VENDEDORES)])
        self.filtro.setToolTip("Mostrar só o que foi registrado por uma pessoa")
        self.filtro.setMinimumWidth(150)
        self.filtro.currentTextChanged.connect(self.filtrar)
        canto = QLabel(f"{self.vendedor}   ·   v{__version__}", objectName="canto")
        canto.setToolTip("Quem está usando (nome do usuário do Windows) e a versão do programa")
        topo.addWidget(self.botao_tema)
        topo.addSpacing(12)
        topo.addWidget(self.rotulo_filtro)
        topo.addWidget(QLabel("Registrado por", objectName="rotulo"))
        topo.addWidget(self.filtro)
        topo.addStretch()
        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(canto)
        geral.addLayout(topo)
        # Aviso amarelo (ex.: "ANA está mexendo neste pedido agora"); some sozinho.
        self.aviso = RotuloAviso("aviso_topo")
        self.apagar_aviso = QTimer(self, singleShot=True, interval=10_000)
        self.apagar_aviso.timeout.connect(lambda: self.aviso.mostrar(""))
        geral.addWidget(self.aviso)

        self.abas = QTabWidget()
        self.abas.setIconSize(QSize(22, 22))
        self.aba_pedidos = AbaPedidos(repo, self.vendedor)
        self.aba_planos = AbaPlanos(repo, self.vendedor)
        self.aba_agenda = AbaAgenda(repo)
        self.aba_lixeira = AbaLixeira(repo)
        for aba in (self.aba_pedidos, self.aba_planos):
            aba.avisar.connect(self.mostrar_aviso)
            aba.mudou.connect(self.aba_lixeira.recarregar)
        for aba in (self.aba_pedidos, self.aba_planos, self.aba_agenda):
            self.aba_lixeira.mudou.connect(aba.recarregar)
        # A Agenda abre pedidos/planos pelas outras abas e se redesenha quando algo é salvo.
        self.aba_agenda.abrir_pedido.connect(self.aba_pedidos.abrir_id)
        self.aba_agenda.abrir_plano.connect(self.aba_planos.abrir_id)
        self.aba_pedidos.mudou.connect(self.aba_agenda.recarregar)
        self.aba_planos.mudou.connect(self.aba_agenda.recarregar)
        self.abas.addTab(self.aba_agenda, ABAS[0][0])
        self.abas.addTab(self.aba_pedidos, ABAS[1][0])
        self.abas.addTab(self.aba_planos, ABAS[2][0])
        self.abas.addTab(self.aba_lixeira, ABAS[3][0])
        geral.addWidget(self.abas)

        self.pintar_icones()

    def mostrar_aviso(self, texto: str) -> None:
        self.aviso.mostrar(texto)
        self.apagar_aviso.start()

    def filtrar(self, texto: str) -> None:
        nome = "" if texto == TODOS else texto
        for aba in (self.aba_agenda, self.aba_pedidos, self.aba_planos, self.aba_lixeira):
            aba.filtro_vendedor = nome
        self.aba_agenda.desenhar()
        self.aba_pedidos.preencher()
        self.aba_planos.preencher()
        self.aba_lixeira.preencher()

    def pintar_icones(self) -> None:
        for i, (_, nome) in enumerate(ABAS):
            self.abas.setTabIcon(i, icone(nome, CORES["destaque"]))
        self.rotulo_filtro.setPixmap(icone("person", CORES["dica"]).pixmap(22, 22))
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
        self.aba_planos.preencher()
        self.aba_agenda.desenhar()
        self.aba_lixeira.preencher()
