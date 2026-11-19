"""Aba Lixeira: pedidos e planos excluídos, para restaurar ou excluir de vez."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from planos_pedidos.dados.repositorio import Repositorio
from planos_pedidos.interface.componentes import botao
from planos_pedidos.regras.formatos import data_tela
from planos_pedidos.regras.vendedor import filtrar_por_vendedor


def _quando(texto: str) -> str:
    """'2026-11-19T14:05:00' → '19/11/2026 14:05'."""
    data, _, hora = texto.partition("T")
    ano, mes, dia = data.split("-")
    return f"{dia}/{mes}/{ano} {hora[:5]}".strip()


class AbaLixeira(QWidget):
    mudou = Signal()
    COLUNAS = ["Tipo", "Nº do pedido / lote", "Cliente", "Data", "Registrado por",
               "Excluído em", "Excluído por"]

    def __init__(self, repo: Repositorio, parent=None) -> None:
        super().__init__(parent)
        self.repo = repo
        self.filtro_vendedor = ""
        self.visiveis: list = []

        geral = QVBoxLayout(self)
        geral.setContentsMargins(14, 14, 14, 14)
        topo = QHBoxLayout()
        explicacao = QLabel("Pedidos e planos excluídos ficam aqui. Escolha um na lista para "
                            "restaurar ou excluir de vez.", objectName="dica")
        self.atualizar = botao("Atualizar", "refresh")
        self.atualizar.setToolTip("Buscar no banco o que os colegas excluíram agora")
        self.atualizar.clicked.connect(self.recarregar)
        self.restaurar = botao("Restaurar", "restore_from_trash")
        self.restaurar.setToolTip("Devolver para a lista (e para a Agenda)")
        self.restaurar.clicked.connect(self._restaurar)
        self.apagar = botao("Excluir de vez", "delete_forever")
        self.apagar.setToolTip("Apagar para sempre (não dá para desfazer)")
        self.apagar.clicked.connect(self._excluir_de_vez)
        topo.addWidget(explicacao, 1)
        for b in (self.atualizar, self.restaurar, self.apagar):
            topo.addWidget(b)
        geral.addLayout(topo)

        self.tabela = QTableWidget(0, len(self.COLUNAS))
        self.tabela.setHorizontalHeaderLabels(self.COLUNAS)
        self.tabela.verticalHeader().hide()
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setShowGrid(False)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.viewport().setCursor(Qt.PointingHandCursor)
        cab = self.tabela.horizontalHeader()
        cab.setSectionResizeMode(QHeaderView.ResizeToContents)
        cab.setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabela.itemSelectionChanged.connect(self._botoes)
        geral.addWidget(self.tabela)
        self.vazio = QLabel("A Lixeira está vazia.", objectName="dica")
        self.vazio.setAlignment(Qt.AlignCenter)
        geral.addWidget(self.vazio)
        self.recarregar()

    def recarregar(self) -> None:
        self.todos = self.repo.lixeira()
        self.preencher()

    def preencher(self) -> None:
        registros = filtrar_por_vendedor([r[1] for r in self.todos], self.filtro_vendedor)
        ids = {id(r) for r in registros}
        self.visiveis = [r for r in self.todos if id(r[1]) in ids]
        self.tabela.setRowCount(len(self.visiveis))
        for linha, (tipo, reg, quando, quem) in enumerate(self.visiveis):
            titulo = reg.numero if tipo == "pedido" else (reg.lote or reg.item)
            textos = ["Pedido" if tipo == "pedido" else "Plano de corte", titulo, reg.cliente,
                      data_tela(reg.data), reg.vendedor, _quando(quando), quem]
            for col, texto in enumerate(textos):
                self.tabela.setItem(linha, col, QTableWidgetItem(texto))
        self.tabela.setVisible(bool(self.visiveis))
        self.vazio.setVisible(not self.visiveis)
        self._botoes()

    def _escolhido(self):
        linhas = self.tabela.selectionModel().selectedRows()
        return self.visiveis[linhas[0].row()] if linhas else None

    def _botoes(self) -> None:
        tem = self._escolhido() is not None
        self.restaurar.setEnabled(tem)
        self.apagar.setEnabled(tem)

    def _restaurar(self) -> None:
        escolhido = self._escolhido()
        if escolhido:
            self.repo.restaurar(escolhido[0], escolhido[1].id)
            self.recarregar()
            self.mudou.emit()

    def _excluir_de_vez(self) -> None:
        escolhido = self._escolhido()
        if not escolhido:
            return
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Excluir de vez")
        caixa.setText("Apagar para sempre? Isso não dá para desfazer.")
        sim = caixa.addButton("Excluir de vez", QMessageBox.DestructiveRole)
        caixa.addButton("Cancelar", QMessageBox.RejectRole)
        caixa.exec()
        if caixa.clickedButton() is sim:
            self.repo.excluir_de_vez(escolhido[0], escolhido[1].id)
            self.recarregar()
