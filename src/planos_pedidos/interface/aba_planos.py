"""Aba Planos de corte: lista dos planos e a janela de cadastro de um plano."""

import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from planos_pedidos.dados.repositorio import Repositorio
from planos_pedidos.interface.componentes import (
    CampoComSugestoes,
    CampoData,
    RotuloAviso,
    botao,
    caixa_atendido,
    celula_situacao,
    confirmar_cliente_novo,
    texto_aviso_cliente,
)
from planos_pedidos.interface.edicao import abrir_com_trava, confirmar_exclusao
from planos_pedidos.interface.estilo import CORES
from planos_pedidos.interface.icones import por_icone
from planos_pedidos.regras.formatos import chave, data_tela
from planos_pedidos.regras.planos import (
    Plano,
    entrega_tela,
    problemas_do_plano,
    quantidade_tela,
)
from planos_pedidos.regras.vendedor import filtrar_por_vendedor


def _rotulo(texto: str) -> QLabel:
    return QLabel(texto, objectName="rotulo")


class JanelaPlano(QDialog):
    """Cadastro e alteração de um plano de corte."""

    def __init__(self, repo: Repositorio, vendedor: str, plano: Plano | None = None,
                 parent=None) -> None:
        super().__init__(parent)
        self.repo = repo
        self.quem = vendedor
        novo = plano is None
        self.plano = plano or Plano(vendedor=vendedor)
        self.setWindowTitle("Novo plano de corte" if novo else "Plano de corte")
        self.setMinimumWidth(1300)

        geral = QVBoxLayout(self)
        geral.setContentsMargins(18, 14, 18, 14)
        caixa = QGroupBox("PLANO DE CORTE")
        grade = QGridLayout(caixa)
        grade.setHorizontalSpacing(14)
        grade.setVerticalSpacing(6)

        self.data = CampoData(com_hoje=True)
        self.cliente = CampoComSugestoes()
        self.cliente.setPlaceholderText("Comece a digitar o nome do cliente")
        self.cliente.definir_opcoes(repo.clientes())
        self.cliente.textChanged.connect(
            lambda: self.aviso_cliente.mostrar(texto_aviso_cliente(self.cliente)))
        self.aviso_cliente = RotuloAviso("aviso")
        self.item = QLineEdit()
        self.lote = QLineEdit()
        self.lote.setToolTip("Volume ou lote")
        registrado = QLabel(self.plano.vendedor or "—", objectName="vendedor")
        registrado.setToolTip("Preenchido sozinho com o nome do usuário do Windows de quem "
                              "cadastrou o plano")
        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Cole aqui a descrição do item que está no sistema")
        self.bobina = QLineEdit()
        self.bobina.setPlaceholderText("Cole aqui a bobina mãe que está no sistema")
        self.quantidade = QLineEdit()
        self.quantidade.setToolTip("Em kg (ex.: 2.000). Também aceita texto, como "
                                   "\"1 un\" ou \"saldo total\"")
        self.quantidade.setMaximumWidth(200)
        self.dica_quantidade = RotuloAviso("dica")
        self.quantidade.textChanged.connect(self._mostrar_quantidade)
        self.entrega = CampoData()
        self.critico = QCheckBox("Crítico")
        self.critico.setToolTip('Marque quando a entrega for crítica (aparece "CRÍTICO" '
                                "ao lado da data)")
        self.entrega.layout().addWidget(self.critico)
        self.observacoes = QLineEdit()
        self.atendido = caixa_atendido("Marque quando o plano de corte estiver atendido "
                                       "(desmarcado = em aberto)")

        # Linha 1: data, cliente, item, lote, quem registrou
        for col, texto in enumerate(["Data do plano", "Cliente", "Código do item", "Volume / lote",
                                     "Registrado por", "Situação"]):
            grade.addWidget(_rotulo(texto), 0, col)
        grade.addWidget(self.data, 1, 0)
        grade.addWidget(self.cliente, 1, 1)
        grade.addWidget(self.item, 1, 2)
        grade.addWidget(self.lote, 1, 3)
        grade.addWidget(registrado, 1, 4)
        grade.addWidget(self.atendido, 1, 5)
        grade.addWidget(self.aviso_cliente, 2, 1, 1, 3)
        # Linha 2: descrição e bobina mãe (texto livre, largo)
        grade.addWidget(_rotulo("Descrição do item"), 3, 0, 1, 2)
        grade.addWidget(_rotulo("Bobina mãe"), 3, 2, 1, 3)
        grade.addWidget(self.descricao, 4, 0, 1, 2)
        grade.addWidget(self.bobina, 4, 2, 1, 3)
        # Linha 3: quantidade, data de entrega, observações
        grade.addWidget(_rotulo("Quantidade (kg)"), 5, 0)
        grade.addWidget(_rotulo("Data de entrega"), 5, 1)
        grade.addWidget(_rotulo("Observações"), 5, 2, 1, 3)
        grade.addWidget(self.quantidade, 6, 0)
        grade.addWidget(self.entrega, 6, 1, Qt.AlignLeft)
        grade.addWidget(self.observacoes, 6, 2, 1, 3)
        grade.addWidget(self.dica_quantidade, 7, 0)
        grade.setColumnStretch(1, 2)
        grade.setColumnStretch(2, 1)
        grade.setColumnStretch(3, 1)
        geral.addWidget(caixa)

        self.erros = RotuloAviso("erro")
        geral.addWidget(self.erros)
        geral.addStretch()
        rodape = QHBoxLayout()
        if not novo:
            excluir = botao("Excluir", "delete")
            excluir.setToolTip("Mandar para a Lixeira (dá para restaurar depois)")
            excluir.clicked.connect(self.excluir)
            rodape.addWidget(excluir)
        rodape.addStretch()
        cancelar = botao("Cancelar", "close")
        cancelar.clicked.connect(self.reject)
        salvar = botao("SALVAR PLANO", "save", objeto="acao")
        salvar.clicked.connect(self.salvar)
        rodape.addWidget(cancelar)
        rodape.addWidget(salvar)
        geral.addLayout(rodape)

        if novo:
            self.data.definir(datetime.date.today())
        else:
            p = self.plano
            self.data.definir(p.data)
            self.cliente.setText(p.cliente)
            self.item.setText(p.item)
            self.lote.setText(p.lote)
            self.descricao.setText(p.descricao)
            self.bobina.setText(p.bobina_mae)
            self.quantidade.setText(p.quantidade)
            self.entrega.definir(p.entrega)
            self.observacoes.setText(p.observacoes)
            self.critico.setChecked(p.critico)
            self.atendido.setChecked(p.atendido)

    def _mostrar_quantidade(self) -> None:
        """Mostra embaixo como vai ficar: "2.000 kg" (só quando muda algo)."""
        texto = self.quantidade.text().strip()
        tela = quantidade_tela(texto)
        self.dica_quantidade.mostrar(f"Vai aparecer: {tela}" if texto and tela != texto else "")

    def ler_plano(self) -> tuple[Plano, list[str]]:
        avisos = []
        datas = {}
        invalidas = []  # data digitada errada: não repetir "falta a data" para ela
        for nome, campo in (("do plano", self.data), ("de entrega", self.entrega)):
            try:
                datas[nome] = campo.data()
            except ValueError:
                datas[nome] = None
                invalidas.append(f"data {nome}")
                avisos.append(f"Data {nome} inválida (use dd/mm/aaaa).")
        plano = Plano(data=datas["do plano"], cliente=self.cliente.nome(),
                      item=self.item.text().strip(), lote=self.lote.text().strip(),
                      descricao=self.descricao.text().strip(),
                      bobina_mae=self.bobina.text().strip(),
                      quantidade=self.quantidade.text().strip(), entrega=datas["de entrega"],
                      observacoes=self.observacoes.text().strip(),
                      critico=self.critico.isChecked(), atendido=self.atendido.isChecked(),
                      vendedor=self.plano.vendedor,
                      id=self.plano.id)
        problemas = [p for p in problemas_do_plano(plano)
                     if not any(i in p for i in invalidas)]
        return plano, avisos + problemas

    def salvar(self) -> None:
        plano, avisos = self.ler_plano()
        if avisos:
            self.erros.mostrar("\n".join(avisos))
            return
        self.erros.mostrar("")
        existente = self.cliente.existente()
        if existente:
            plano.cliente = existente
        elif not confirmar_cliente_novo(self, plano.cliente):
            self.cliente.setFocus()
            self.cliente.mostrar_sugestoes()
            return
        plano.cliente = self.repo.adicionar_cliente(plano.cliente)
        self.repo.salvar_plano(plano, quem=self.quem)
        self.plano = plano
        self.accept()

    def excluir(self) -> None:
        if confirmar_exclusao(self, "este plano de corte"):
            self.repo.excluir("plano", self.plano.id, quem=self.quem)
            self.accept()


class AbaPlanos(QWidget):
    """Lista de todos os planos de corte, com pesquisa; clicar na linha abre o plano."""

    mudou = Signal()
    avisar = Signal(str)  # aviso amarelo no alto da janela (ex.: plano em uso)
    COLUNAS = ["Data", "Cliente", "Código do item", "Volume / lote", "Descrição do item",
               "Bobina mãe",
               "Quantidade", "Entrega", "Observações", "Situação", "Registrado por"]

    def __init__(self, repo: Repositorio, vendedor: str, parent=None) -> None:
        super().__init__(parent)
        self.repo = repo
        self.vendedor = vendedor
        self.filtro_vendedor = ""  # "" = todos
        self.planos: list[Plano] = []
        self.visiveis: list[Plano] = []

        geral = QVBoxLayout(self)
        geral.setContentsMargins(14, 14, 14, 14)
        topo = QHBoxLayout()
        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText(
            "Pesquisar por cliente, item, lote, descrição ou bobina mãe")
        self.pesquisa.setClearButtonEnabled(True)
        lupa = self.pesquisa.addAction(QIcon(), QLineEdit.LeadingPosition)
        por_icone(lupa, "search", "dica", CORES)
        self.pesquisa.textChanged.connect(self.preencher)
        self.atualizar = botao("Atualizar", "refresh")
        self.atualizar.setToolTip("Buscar no banco os planos que os colegas lançaram "
                                  "ou mudaram agora")
        self.atualizar.clicked.connect(self.recarregar)
        self.novo = botao("Novo plano", "add", objeto="acao")
        self.novo.clicked.connect(self.novo_plano)
        topo.addWidget(self.pesquisa, 1)
        topo.addWidget(self.atualizar)
        topo.addWidget(self.novo)
        geral.addLayout(topo)

        self.tabela = QTableWidget(0, len(self.COLUNAS))
        self.tabela.setHorizontalHeaderLabels(self.COLUNAS)
        self.tabela.verticalHeader().hide()
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setShowGrid(False)
        self.tabela.setAlternatingRowColors(True)  # listras leves, como no Excel
        self.tabela.setMouseTracking(True)
        self.tabela.viewport().setCursor(Qt.PointingHandCursor)
        cab = self.tabela.horizontalHeader()
        cab.setSectionResizeMode(QHeaderView.ResizeToContents)
        cab.setSectionResizeMode(4, QHeaderView.Stretch)
        cab.setSectionResizeMode(5, QHeaderView.Stretch)
        self.tabela.cellClicked.connect(lambda linha, _c: self.abrir(linha))
        geral.addWidget(self.tabela)
        self.vazio = QLabel("Nenhum plano de corte ainda. Clique em \"Novo plano\" para "
                            "começar.", objectName="dica")
        self.vazio.setAlignment(Qt.AlignCenter)
        geral.addWidget(self.vazio)
        self.recarregar()

    def recarregar(self) -> None:
        self.planos = self.repo.planos()
        self.preencher()

    def preencher(self) -> None:
        procurado = chave(self.pesquisa.text())
        self.visiveis = [
            p for p in filtrar_por_vendedor(self.planos, self.filtro_vendedor)
            if procurado in chave(" ".join([p.cliente, p.item, p.lote, p.descricao,
                                            p.bobina_mae, p.observacoes, p.vendedor]))]
        self.tabela.setRowCount(len(self.visiveis))
        for linha, p in enumerate(self.visiveis):
            textos = [data_tela(p.data), p.cliente, p.item, p.lote, p.descricao, p.bobina_mae,
                      quantidade_tela(p.quantidade), entrega_tela(p), p.observacoes,
                      None, p.vendedor]
            for col, texto in enumerate(textos):
                celula = (celula_situacao(p.atendido) if texto is None
                          else QTableWidgetItem(texto))
                if col == 6:
                    celula.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if col in (4, 5, 8):
                    celula.setToolTip(texto)
                self.tabela.setItem(linha, col, celula)
        self.tabela.setVisible(bool(self.planos))
        self.vazio.setVisible(not self.planos)

    def _abrir_janela(self, plano: Plano | None) -> None:
        janela = JanelaPlano(self.repo, self.vendedor, plano, parent=self)
        if plano is None:
            mudou = bool(janela.exec())
        else:
            mudou, aviso = abrir_com_trava(self.repo, "plano", plano.id, self.vendedor, janela)
            if aviso:
                self.avisar.emit(aviso)
        if mudou:
            self.recarregar()
            self.mudou.emit()

    def novo_plano(self) -> None:
        self._abrir_janela(None)

    def abrir(self, linha: int) -> None:
        self.abrir_id(self.visiveis[linha].id)

    def abrir_id(self, plano_id: int) -> None:
        """Abre o plano pelo número interno (usado também pela Agenda)."""
        plano = self.repo.plano(plano_id)
        if plano is not None:
            self._abrir_janela(plano)
