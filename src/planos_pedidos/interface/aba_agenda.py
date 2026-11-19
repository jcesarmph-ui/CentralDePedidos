"""Aba Agenda: calendário do mês com o que vence em cada dia, e ao lado os atrasados e os
próximos 7 dias. Clicar numa etiqueta abre o pedido/plano; clicar no dia mostra tudo dele.
"""

import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from planos_pedidos.dados.repositorio import Repositorio
from planos_pedidos.interface.componentes import botao
from planos_pedidos.interface.estilo import ATRASADO, CORES, ENTREGUE, HOJE
from planos_pedidos.interface.icones import por_icone
from planos_pedidos.regras.agenda import (
    Evento,
    Situacao,
    Tipo,
    atrasados,
    montar_eventos,
    proximos,
    semanas_do_mes,
)
from planos_pedidos.regras.formatos import data_tela, kg
from planos_pedidos.regras.vendedor import filtrar_por_vendedor

MESES = ["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO",
         "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
DIAS_SEMANA = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
VISIVEIS_NO_DIA = 3  # etiquetas por quadradinho; o resto vira "+N mais"

# Tracinho à esquerda da etiqueta: diferencia pedido de plano sem precisar de ícone.
COR_TIPO = {Tipo.PEDIDO: "#60a5fa", Tipo.PLANO: "#c084fc"}
NOME_TIPO = {Tipo.PEDIDO: "Pedido", Tipo.PLANO: "Plano de corte"}


def _cores(evento: Evento) -> tuple[str, str]:
    """(fundo, letra) da etiqueta conforme a situação do prazo."""
    if evento.situacao == Situacao.ATRASADO:
        return ATRASADO
    if evento.situacao == Situacao.PERTO:
        return HOJE
    if evento.situacao == Situacao.ENTREGUE:
        return ENTREGUE
    if evento.situacao == Situacao.PASSOU:
        return CORES["campo"], CORES["dica"]
    return CORES["campo"], CORES["texto"]


class Etiqueta(QPushButton):
    """Um pedido/plano num dia. O texto encolhe com "…" quando não cabe."""

    abrir = Signal(object)

    def __init__(self, evento: Evento, com_data: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.evento = evento
        texto = f"{evento.titulo} · {evento.cliente}" if evento.titulo else evento.cliente
        if evento.critico:
            texto = f"CRÍTICO · {texto}"
        if com_data:
            texto += f" · {data_tela(evento.data)[:5]}"
        self.texto = texto
        self.setObjectName("etiqueta")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        fundo, letra = _cores(evento)
        negrito = "bold" if evento.critico or evento.situacao == Situacao.ATRASADO else "normal"
        self.setStyleSheet(
            f"QPushButton#etiqueta {{ background: {fundo}; color: {letra}; "
            f"border: none; border-left: 4px solid {COR_TIPO[evento.tipo]}; "
            f"font-weight: {negrito}; }}")
        if evento.situacao == Situacao.ATRASADO:
            por_icone(self, "schedule", "branco", CORES, 16)
        elif evento.situacao == Situacao.ENTREGUE:
            por_icone(self, "check", "branco", CORES, 16)
        quanto = f"{kg(evento.kg)} kg" if evento.kg else ""
        rotulo_kg = "falta" if evento.tipo == Tipo.PEDIDO else "quantidade"
        self.setToolTip(
            f"{NOME_TIPO[evento.tipo]} {evento.titulo} — {evento.cliente}\n"
            f"Entrega: {data_tela(evento.data)} ({evento.situacao})"
            + (" — CRÍTICO" if evento.critico else "")
            + (f"\n{rotulo_kg.capitalize()}: {quanto}" if quanto else "")
            + (f"\nRegistrado por: {evento.vendedor}" if evento.vendedor else "")
            + (f"\n\n{evento.detalhe}" if evento.detalhe else "")
            + "\n\nClique para abrir")
        self.clicked.connect(lambda: self.abrir.emit(self.evento))
        self.setText(texto)

    def resizeEvent(self, evento) -> None:  # noqa: N802 — nome do Qt
        super().resizeEvent(evento)
        sobra = self.width() - 18 - (self.iconSize().width() if not self.icon().isNull() else 0)
        self.setText(self.fontMetrics().elidedText(self.texto, Qt.ElideRight, max(sobra, 10)))


class QuadradoDia(QFrame):
    """Um dia do calendário: número, etiquetas, "+N mais" e total de kg do dia."""

    clicado = Signal(object)

    def __init__(self, dia: datetime.date, eventos: list[Evento], do_mes: bool,
                 hoje: datetime.date, ao_abrir) -> None:
        super().__init__()
        self.dia = dia
        nome = "diahoje" if dia == hoje else ("dia" if do_mes else "dia_fora")
        self.setObjectName(nome)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        self.setToolTip("Clique para ver tudo deste dia")
        v = QVBoxLayout(self)
        v.setContentsMargins(6, 4, 6, 4)
        v.setSpacing(3)
        numero = QLabel(f"{dia.day}  HOJE" if dia == hoje else str(dia.day),
                        objectName="num_hoje" if dia == hoje else "num_dia")
        v.addWidget(numero)
        for evento in eventos[:VISIVEIS_NO_DIA]:
            etiqueta = Etiqueta(evento)
            etiqueta.abrir.connect(ao_abrir)
            v.addWidget(etiqueta)
        if len(eventos) > VISIVEIS_NO_DIA:
            mais = QPushButton(f"+{len(eventos) - VISIVEIS_NO_DIA} mais", objectName="mais")
            mais.setCursor(Qt.PointingHandCursor)
            mais.clicked.connect(lambda: self.clicado.emit(self.dia))
            v.addWidget(mais, 0, Qt.AlignLeft)
        v.addStretch()
        total = sum(e.kg for e in eventos if e.situacao != Situacao.ENTREGUE)
        if total:
            rodape = QLabel(f"{kg(total)} kg", objectName="kg_dia")
            rodape.setAlignment(Qt.AlignRight)
            rodape.setToolTip("Total de kg que sai neste dia (sem o que já foi entregue)")
            v.addWidget(rodape)

    def mousePressEvent(self, evento) -> None:  # noqa: N802 — nome do Qt
        self.clicado.emit(self.dia)
        super().mousePressEvent(evento)


class JanelaDia(QDialog):
    """Tudo o que vence num dia, sem o limite do quadradinho."""

    def __init__(self, dia: datetime.date, eventos: list[Evento], ao_abrir, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Entregas de {data_tela(dia)}")
        self.setMinimumWidth(560)
        v = QVBoxLayout(self)
        titulo = QLabel(f"{DIAS_SEMANA[dia.weekday()]} · {data_tela(dia)}", objectName="mes")
        v.addWidget(titulo)
        if not eventos:
            v.addWidget(QLabel("Nada vence neste dia.", objectName="dica"))
        for evento in eventos:
            etiqueta = Etiqueta(evento)
            etiqueta.setMinimumHeight(32)
            etiqueta.abrir.connect(lambda e: (self.accept(), ao_abrir(e)))
            v.addWidget(etiqueta)
        total = sum(e.kg for e in eventos if e.situacao != Situacao.ENTREGUE)
        if total:
            v.addWidget(QLabel(f"Total do dia: {kg(total)} kg", objectName="kg_dia"))
        fechar = botao("Fechar", "close")
        fechar.clicked.connect(self.reject)
        v.addWidget(fechar, 0, Qt.AlignRight)


class AbaAgenda(QWidget):
    abrir_pedido = Signal(int)
    abrir_plano = Signal(int)

    def __init__(self, repo: Repositorio, parent=None) -> None:
        super().__init__(parent)
        self.repo = repo
        hoje = datetime.date.today()
        self.ano, self.mes = hoje.year, hoje.month
        self.eventos: list[Evento] = []
        self.filtro_vendedor = ""  # "" = todos

        geral = QHBoxLayout(self)
        geral.setContentsMargins(14, 14, 14, 14)
        geral.setSpacing(14)

        # Coluna da esquerda: atrasados e próximos 7 dias (sempre à vista).
        self.lado = QFrame(objectName="painel_lado")
        self.lado.setFixedWidth(330)
        lv = QVBoxLayout(self.lado)
        lv.setContentsMargins(10, 10, 10, 10)
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        self.lista_lado = QWidget(objectName="rolagem")
        self.lista_layout = QVBoxLayout(self.lista_lado)
        self.lista_layout.setContentsMargins(0, 0, 0, 0)
        self.lista_layout.setSpacing(4)
        rolagem.setWidget(self.lista_lado)
        lv.addWidget(rolagem)
        geral.addWidget(self.lado)

        # Direita: navegação do mês e o calendário.
        direita = QVBoxLayout()
        nav = QHBoxLayout()
        self.anterior = QToolButton(objectName="nav")
        por_icone(self.anterior, "chevron_left", "texto", CORES, 26)
        self.anterior.setToolTip("Mês anterior")
        self.anterior.clicked.connect(lambda: self.mudar_mes(-1))
        self.botao_hoje = QPushButton("HOJE")
        self.botao_hoje.setToolTip("Voltar para o mês de hoje")
        self.botao_hoje.clicked.connect(self.ir_para_hoje)
        self.proximo = QToolButton(objectName="nav")
        por_icone(self.proximo, "chevron_right", "texto", CORES, 26)
        self.proximo.setToolTip("Próximo mês")
        self.proximo.clicked.connect(lambda: self.mudar_mes(1))
        self.titulo_mes = QLabel(objectName="mes")
        self.ver_pedidos = QCheckBox("Pedidos")
        self.ver_planos = QCheckBox("Planos de corte")
        for caixa in (self.ver_pedidos, self.ver_planos):
            caixa.setChecked(True)
            caixa.toggled.connect(self.desenhar)
        self.ver_pedidos.setToolTip("Mostrar os pedidos (tracinho azul)")
        self.ver_planos.setToolTip("Mostrar os planos de corte (tracinho roxo)")
        self.atualizar = botao("Atualizar", "refresh")
        self.atualizar.setToolTip("Buscar no banco o que os colegas lançaram ou mudaram agora")
        self.atualizar.clicked.connect(self.recarregar)
        for w in (self.anterior, self.botao_hoje, self.proximo, self.titulo_mes):
            nav.addWidget(w)
        nav.addStretch()
        nav.addWidget(self._legenda())
        nav.addSpacing(16)
        nav.addWidget(self.ver_pedidos)
        nav.addWidget(self.ver_planos)
        nav.addWidget(self.atualizar)
        direita.addLayout(nav)

        self.grade = QGridLayout()
        self.grade.setSpacing(6)
        for c, nome in enumerate(DIAS_SEMANA):
            r = QLabel(nome, objectName="semana")
            r.setAlignment(Qt.AlignCenter)
            self.grade.addWidget(r, 0, c)
            self.grade.setColumnStretch(c, 1)
        for linha in range(1, 7):
            self.grade.setRowStretch(linha, 1)
        direita.addLayout(self.grade, 1)
        geral.addLayout(direita, 1)
        self.recarregar()

    def _legenda(self) -> QLabel:
        partes = []
        for nome, (fundo, _) in (("atrasado", ATRASADO), ("hoje/amanhã", HOJE),
                                 ("entregue", ENTREGUE)):
            partes.append(f"<span style='color:{fundo}; font-size:14pt'>■</span> {nome}")
        partes.append(f"<span style='color:{COR_TIPO[Tipo.PEDIDO]}; font-size:14pt'>▎</span>"
                      " pedido")
        partes.append(f"<span style='color:{COR_TIPO[Tipo.PLANO]}; font-size:14pt'>▎</span>"
                      " plano")
        legenda = QLabel("&nbsp;&nbsp;&nbsp;".join(partes), objectName="legenda")
        return legenda

    # ------------------------------------------------------------------ dados
    def recarregar(self) -> None:
        self.eventos = montar_eventos(self.repo.pedidos(), self.repo.planos())
        self.desenhar()

    def _filtrados(self) -> list[Evento]:
        tipos = set()
        if self.ver_pedidos.isChecked():
            tipos.add(Tipo.PEDIDO)
        if self.ver_planos.isChecked():
            tipos.add(Tipo.PLANO)
        return [e for e in filtrar_por_vendedor(self.eventos, self.filtro_vendedor)
                if e.tipo in tipos]

    # ------------------------------------------------------------------ desenho
    def desenhar(self) -> None:
        hoje = datetime.date.today()
        eventos = self._filtrados()
        self.titulo_mes.setText(f"{MESES[self.mes - 1]} {self.ano}")
        self._desenhar_lado(eventos, hoje)
        while self.grade.count() > 7:  # mantém só os nomes dos dias da semana
            w = self.grade.takeAt(7).widget()
            if w:
                w.deleteLater()
        por_dia: dict[datetime.date, list[Evento]] = {}
        for e in eventos:
            por_dia.setdefault(e.data, []).append(e)
        for s, semana in enumerate(semanas_do_mes(self.ano, self.mes)):
            for d, dia in enumerate(semana):
                quadrado = QuadradoDia(dia, por_dia.get(dia, []), dia.month == self.mes, hoje,
                                       self.abrir_evento)
                quadrado.clicado.connect(self.abrir_dia)
                self.grade.addWidget(quadrado, s + 1, d)

    def _desenhar_lado(self, eventos: list[Evento], hoje: datetime.date) -> None:
        while self.lista_layout.count():
            item = self.lista_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():  # linha de título (ícone + texto)
                while item.layout().count():
                    filho = item.layout().takeAt(0).widget()
                    if filho:
                        filho.deleteLater()
        secoes = [("ATRASADOS", "schedule", atrasados(eventos)),
                  ("PRÓXIMOS 7 DIAS", "calendar_month", proximos(eventos, hoje))]
        for titulo, icone_nome, lista in secoes:
            cab = QHBoxLayout()
            cab.setSpacing(6)
            simbolo = QLabel()
            por_icone(simbolo, icone_nome, "texto", CORES, 20)
            cab.addWidget(simbolo)
            cab.addWidget(QLabel(f"{titulo} ({len(lista)})", objectName="secao"))
            cab.addStretch()
            self.lista_layout.addLayout(cab)
            if not lista:
                vazio = QLabel("Nada por aqui.", objectName="dica")
                self.lista_layout.addWidget(vazio)
            for evento in lista:
                etiqueta = Etiqueta(evento, com_data=True)
                etiqueta.abrir.connect(self.abrir_evento)
                self.lista_layout.addWidget(etiqueta)
            self.lista_layout.addSpacing(10)
        self.lista_layout.addStretch()

    # ------------------------------------------------------------------ ações
    def mudar_mes(self, passo: int) -> None:
        mes = self.mes + passo
        self.ano += (mes - 1) // 12
        self.mes = (mes - 1) % 12 + 1
        self.desenhar()

    def ir_para_hoje(self) -> None:
        hoje = datetime.date.today()
        self.ano, self.mes = hoje.year, hoje.month
        self.desenhar()

    def abrir_evento(self, evento: Evento) -> None:
        if evento.tipo == Tipo.PEDIDO:
            self.abrir_pedido.emit(evento.id)
        else:
            self.abrir_plano.emit(evento.id)

    def abrir_dia(self, dia: datetime.date) -> None:
        eventos = [e for e in self._filtrados() if e.data == dia]
        JanelaDia(dia, eventos, self.abrir_evento, parent=self).exec()
