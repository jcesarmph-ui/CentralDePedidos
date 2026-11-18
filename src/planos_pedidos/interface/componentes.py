"""Peças de tela usadas em mais de uma aba (adaptadas do SistemaCalibracao)."""

import datetime
import difflib

from PySide6.QtCore import QEvent, QObject, QPoint, QStringListModel, Qt
from PySide6.QtGui import QColor, QTextCharFormat
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractSpinBox,
    QApplication,
    QCalendarWidget,
    QComboBox,
    QCompleter,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabBar,
    QToolButton,
    QWidget,
)

from planos_pedidos.interface.estilo import CORES
from planos_pedidos.interface.icones import por_icone
from planos_pedidos.regras.formatos import chave, data_tela, ler_data


class FiltroRodaDoMouse(QObject):
    """A roda do mouse só rola a tela: nunca troca opção, data ou aba. Também põe a mãozinha
    em tudo o que é clicável."""

    SEM_RODA = (QComboBox, QAbstractSpinBox, QTabBar)
    CLICAVEIS = (QAbstractButton, QComboBox, QTabBar)

    def eventFilter(self, objeto, evento) -> bool:  # noqa: N802 — nome exigido pelo Qt
        if evento.type() == QEvent.Polish and isinstance(objeto, self.CLICAVEIS):
            objeto.setCursor(Qt.PointingHandCursor)
        if evento.type() == QEvent.Wheel and isinstance(objeto, self.SEM_RODA):
            pai = objeto.parentWidget()
            if pai is not None:
                QApplication.sendEvent(pai, evento)
            return True
        return False


def instalar_filtro_roda() -> None:
    app = QApplication.instance()
    if app is not None and not hasattr(app, "_filtro_roda"):
        app._filtro_roda = FiltroRodaDoMouse(app)
        app.installEventFilter(app._filtro_roda)


def botao(texto: str, nome_icone: str | None = None, objeto: str = "") -> QPushButton:
    """Botão com ícone na frente do texto (o texto continua: ninguém precisa adivinhar)."""
    b = QPushButton(texto)
    if objeto:
        b.setObjectName(objeto)
    if nome_icone:
        por_icone(b, nome_icone, "branco" if objeto == "acao" else "texto", CORES)
    b.setCursor(Qt.PointingHandCursor)
    return b


class CampoComSugestoes(QLineEdit):
    """Sugestões enquanto digita, como a pesquisa do Google: mostra os nomes que têm o que foi
    digitado em qualquer parte, sem ligar para maiúsculas nem acentos."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.opcoes: list[str] = []
        self._modelo = QStringListModel(self)
        self.sugestoes = QCompleter(self._modelo, self)
        self.sugestoes.setWidget(self)
        self.sugestoes.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.sugestoes.setMaxVisibleItems(12)
        self.sugestoes.popup().setObjectName("sugestoes")  # janela solta: regra própria no estilo
        self.sugestoes.activated.connect(self.escolher)
        self.textEdited.connect(self.mostrar_sugestoes)

    def definir_opcoes(self, opcoes: list[str]) -> None:
        self.opcoes = list(opcoes)

    def filtradas(self) -> list[str]:
        procurado = chave(self.text())
        return [o for o in self.opcoes if procurado in chave(o)]

    def mostrar_sugestoes(self, _texto: str = "") -> None:
        filtradas = self.filtradas()
        self._modelo.setStringList(filtradas)
        if filtradas and self.text().strip():
            self.sugestoes.complete()
        else:
            self.sugestoes.popup().hide()

    def escolher(self, opcao: str) -> None:
        self.setText(opcao)
        self.sugestoes.popup().hide()

    def nome(self) -> str:
        return " ".join(self.text().split())

    def existente(self) -> str | None:
        """O nome da lista igual ao digitado (sem ligar para maiúsculas/acentos), se houver."""
        k = chave(self.nome())
        return next((o for o in self.opcoes if chave(o) == k), None)

    def parecidos(self) -> list[str]:
        k = chave(self.nome()).replace(" ", "").replace(".", "")
        if not k:
            return []
        achados = []
        for o in self.opcoes:
            ko = chave(o).replace(" ", "").replace(".", "")
            if k in ko or ko in k or difflib.SequenceMatcher(None, k, ko).ratio() >= 0.75:
                achados.append(o)
        return achados[:4]


class CampoData(QWidget):
    """Data dd/mm/aaaa: dá para digitar ou escolher no calendário (ícone ao lado). Com
    `com_hoje=True`, um botão HOJE preenche a data do dia num clique."""

    def __init__(self, com_hoje: bool = False, parent=None) -> None:
        super().__init__(parent)
        linha = QHBoxLayout(self)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(4)
        self.campo = QLineEdit()
        self.campo.setPlaceholderText("dd/mm/aaaa")
        self.campo.setMinimumWidth(135)
        self.campo.setMaximumWidth(150)
        self.campo.editingFinished.connect(self._completar)
        self.botao_calendario = QToolButton(objectName="calendario")
        por_icone(self.botao_calendario, "calendar_month", "texto", CORES)
        self.botao_calendario.setToolTip("Abrir o calendário (ou digite a data: dd/mm/aaaa)")
        self.botao_calendario.setCursor(Qt.PointingHandCursor)
        self.botao_calendario.clicked.connect(self.abrir)
        linha.addWidget(self.campo)
        linha.addWidget(self.botao_calendario)
        self.botao_hoje = None
        if com_hoje:
            self.botao_hoje = botao("HOJE", "today")
            self.botao_hoje.setToolTip("Preencher com a data de hoje")
            self.botao_hoje.clicked.connect(lambda: self.definir(datetime.date.today()))
            linha.addWidget(self.botao_hoje)
        self.calendario = QCalendarWidget()
        self.calendario.setWindowFlags(Qt.Popup)
        self.calendario.setObjectName("calendario_popup")
        self.calendario.setGridVisible(False)
        self.calendario.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendario.clicked.connect(self._escolheu)

    def pintar_calendario(self) -> None:
        """Fim de semana na mesma cor dos outros dias (vermelho é só para erro)."""
        formato = QTextCharFormat()
        formato.setForeground(QColor(CORES["texto"]))
        for dia in (Qt.Saturday, Qt.Sunday):
            self.calendario.setWeekdayTextFormat(dia, formato)

    def abrir(self) -> None:
        self.pintar_calendario()
        try:
            dia = ler_data(self.campo.text()) or datetime.date.today()
        except ValueError:
            dia = datetime.date.today()
        self.calendario.setSelectedDate(dia)
        self.calendario.adjustSize()
        self.calendario.move(self.campo.mapToGlobal(QPoint(0, self.campo.height())))
        self.calendario.show()

    def _escolheu(self, data) -> None:
        self.definir(data.toPython())
        self.calendario.hide()

    def _completar(self) -> None:
        """"18/11" vira "18/11/2026" ao sair do campo (se for uma data válida)."""
        try:
            dia = ler_data(self.campo.text())
        except ValueError:
            return
        if dia:
            self.campo.setText(data_tela(dia))

    def definir(self, dia: datetime.date | None) -> None:
        self.campo.setText(data_tela(dia))

    def data(self) -> datetime.date | None:
        """A data digitada; ValueError se o texto não for uma data."""
        return ler_data(self.campo.text())


class RotuloAviso(QLabel):
    """Texto de aviso/erro que só ocupa lugar quando tem algo escrito."""

    def __init__(self, objeto: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName(objeto)
        self.setWordWrap(True)
        self.hide()

    def mostrar(self, texto: str) -> None:
        self.setText(texto)
        self.setVisible(bool(texto))
