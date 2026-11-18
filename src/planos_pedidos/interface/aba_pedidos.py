"""Aba Pedidos: lista de pedidos e a janela de cadastro (cabeçalho + vários itens)."""

import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from planos_pedidos.dados.repositorio import Repositorio
from planos_pedidos.interface.componentes import (
    CampoComSugestoes,
    CampoData,
    RotuloAviso,
    botao,
    confirmar_cliente_novo,
    texto_aviso_cliente,
)
from planos_pedidos.interface.estilo import ATRASADO, CORES, ENTREGUE, HOJE
from planos_pedidos.interface.icones import por_icone
from planos_pedidos.regras.formatos import (
    chave,
    data_tela,
    dinheiro,
    kg,
    ler_numero,
    medida,
)
from planos_pedidos.regras.pedidos import (
    Item,
    Pedido,
    Tipo,
    descricao,
    falta,
    falta_total,
    item_entregue,
    prazo_mais_proximo,
    problemas_do_pedido,
)


def _texto_numero(valor: float | None, dinheiro_: bool = False) -> str:
    if valor is None:
        return ""
    if dinheiro_:
        return f"{valor:.2f}".replace(".", ",")
    return kg(valor) if float(valor).is_integer() else medida(valor)


def cores_do_prazo(prazo: datetime.date | None, entregue: bool,
                   hoje: datetime.date | None = None) -> tuple[str, str] | None:
    """Vermelho atrasado, amarelo hoje/amanhã, verde entregue, sem cor no prazo."""
    hoje = hoje or datetime.date.today()
    if entregue:
        return ENTREGUE
    if prazo is None:
        return None
    if prazo < hoje:
        return ATRASADO
    if prazo <= hoje + datetime.timedelta(days=1):
        return HOJE
    return None


# --------------------------------------------------------------------------- linha de item
class LinhaItem:
    """Os campos de um item, postos numa linha da grade de itens."""

    COLUNAS = ["", "Código", "Tipo", "Espessura (mm)", "Largura (mm)", "Comprimento (mm)",
               "Quantidade (kg)", "Prazo de entrega", "1ª entrega (kg)", "2ª entrega (kg)",
               "Falta (kg)", "Preço do kg (R$)", "Observações", ""]

    def __init__(self, ao_mudar, ao_remover) -> None:
        self.numero = QLabel(objectName="rotulo")
        self.codigo = QLineEdit()
        self.tipo = QComboBox()
        self.tipo.addItems([t.value for t in Tipo])
        self.espessura = QLineEdit()
        self.largura = QLineEdit()
        self.comprimento = QLineEdit()
        self.quantidade = QLineEdit()
        self.prazo = CampoData()
        self.entrega1 = QLineEdit()
        self.entrega2 = QLineEdit()
        # Falta: campo igual aos outros, só que calculado (não se digita).
        self.falta = QLineEdit(objectName="falta")
        self.falta.setReadOnly(True)
        self.falta.setFocusPolicy(Qt.NoFocus)
        self.falta.setAlignment(Qt.AlignRight)
        self.falta.setMaximumWidth(125)
        self.falta_check = self.falta.addAction(QIcon(), QLineEdit.LeadingPosition)
        por_icone(self.falta_check, "check", "certo", CORES)
        self.falta_check.setVisible(False)
        self.preco = QLineEdit()
        self.preco.setPlaceholderText("0,00")
        self.observacoes = QLineEdit()
        self.remover = QToolButton(objectName="remover")
        por_icone(self.remover, "delete", "dica", CORES)
        self.remover.setToolTip("Tirar este item do pedido")
        self.remover.clicked.connect(lambda: ao_remover(self))

        # Larguras: números estreitos; Tipo cabe "Chapa"; Observações fica com o que sobra.
        self.codigo.setMinimumWidth(100)
        self.tipo.setMinimumWidth(115)
        self.observacoes.setMinimumWidth(220)
        for campo in (self.espessura, self.largura, self.comprimento, self.quantidade,
                      self.entrega1, self.entrega2, self.preco):
            campo.setAlignment(Qt.AlignRight)
            campo.setMaximumWidth(125)
            campo.textChanged.connect(lambda _t: ao_mudar())
        self.tipo.currentTextChanged.connect(self._tipo_mudou)
        self.tipo.currentTextChanged.connect(lambda _t: ao_mudar())
        self._tipo_mudou(self.tipo.currentText())

    def widgets(self) -> list[QWidget]:
        return [self.numero, self.codigo, self.tipo, self.espessura, self.largura,
                self.comprimento, self.quantidade, self.prazo, self.entrega1, self.entrega2,
                self.falta, self.preco, self.observacoes, self.remover]

    def _tipo_mudou(self, texto: str) -> None:
        """Rolo não tem comprimento: o campo fica apagado."""
        eh_chapa = texto == Tipo.CHAPA.value
        self.comprimento.setEnabled(eh_chapa)
        self.comprimento.setPlaceholderText("" if eh_chapa else "—")
        if not eh_chapa:
            self.comprimento.clear()
        self.comprimento.setToolTip("" if eh_chapa else "Rolo não tem comprimento")

    def preencher(self, item: Item) -> None:
        self.codigo.setText(item.codigo)
        self.tipo.setCurrentText(item.tipo.value)
        self.espessura.setText(medida(item.espessura))
        self.largura.setText(medida(item.largura))
        self.comprimento.setText(medida(item.comprimento))
        self.quantidade.setText(kg(item.quantidade))
        self.prazo.definir(item.prazo)
        self.entrega1.setText(kg(item.entrega1))
        self.entrega2.setText(kg(item.entrega2))
        self.preco.setText(_texto_numero(item.preco_kg, dinheiro_=True))
        self.observacoes.setText(item.observacoes)

    def ler(self) -> tuple[Item, list[str]]:
        """O item digitado e a lista de campos com texto inválido (que ficam em vermelho)."""
        invalidos = []

        def numero(campo: QLineEdit, nome: str) -> float | None:
            try:
                valor = ler_numero(campo.text())
                campo.setProperty("erro", False)
            except ValueError:
                valor = None
                invalidos.append(nome)
                campo.setProperty("erro", True)
            campo.style().unpolish(campo)
            campo.style().polish(campo)
            return valor

        try:
            prazo = self.prazo.data()
            self.prazo.campo.setProperty("erro", False)
        except ValueError:
            prazo = None
            invalidos.append("prazo (use dd/mm/aaaa)")
            self.prazo.campo.setProperty("erro", True)
        self.prazo.campo.style().unpolish(self.prazo.campo)
        self.prazo.campo.style().polish(self.prazo.campo)

        item = Item(
            codigo=self.codigo.text().strip(),
            tipo=Tipo(self.tipo.currentText()),
            espessura=numero(self.espessura, "espessura"),
            largura=numero(self.largura, "largura"),
            comprimento=numero(self.comprimento, "comprimento"),
            quantidade=numero(self.quantidade, "quantidade"),
            prazo=prazo,
            entrega1=numero(self.entrega1, "1ª entrega"),
            entrega2=numero(self.entrega2, "2ª entrega"),
            preco_kg=numero(self.preco, "preço"),
            observacoes=self.observacoes.text().strip(),
        )
        return item, invalidos

    def atualizar_falta(self) -> None:
        """Falta calculada na hora: vermelho enquanto falta; ✔ verde quando entregou tudo
        (também quando passou da quantidade — aí mostra quanto passou, com "+")."""
        item, _ = self.ler()
        f = falta(item)
        entregue = item_entregue(item)
        self.falta_check.setVisible(entregue)
        if f is None:
            texto, estado, dica = "", "", ""
        elif entregue:
            texto = f"+{kg(-f)}" if f < 0 else "0"
            estado = "ok"
            dica = (f"Entregue tudo, com {kg(-f)} kg a mais que o pedido" if f < 0
                    else "Item todo entregue")
        else:
            texto, estado, dica = kg(f), "falta", "Quantidade menos as entregas"
        self.falta.setText(texto)
        self.falta.setToolTip(dica)
        self.falta.setProperty("estado", estado)
        self.falta.style().unpolish(self.falta)
        self.falta.style().polish(self.falta)


# --------------------------------------------------------------------------- janela do pedido
class JanelaPedido(QDialog):
    """Cadastro e alteração de um pedido: os dados do pedido uma vez só e os itens embaixo."""

    def __init__(self, repo: Repositorio, vendedor: str, pedido: Pedido | None = None,
                 parent=None) -> None:
        super().__init__(parent)
        self.repo = repo
        self.pedido = pedido or Pedido(vendedor=vendedor)
        self.quem = vendedor
        novo = pedido is None
        self.setWindowTitle("Novo pedido" if novo else f"Pedido {self.pedido.numero}")
        self.linhas: list[LinhaItem] = []

        geral = QVBoxLayout(self)
        geral.setContentsMargins(18, 14, 18, 14)

        # Faixa 1: dados do pedido
        caixa = QGroupBox("PEDIDO")
        grade = QGridLayout(caixa)
        grade.setHorizontalSpacing(14)
        self.data = CampoData(com_hoje=True)
        self.cliente = CampoComSugestoes()
        self.cliente.setPlaceholderText("Comece a digitar o nome do cliente")
        self.cliente.definir_opcoes(repo.clientes())
        self.cliente.textChanged.connect(self._avisar_cliente)
        self.numero = QLineEdit()
        self.numero.setMaximumWidth(180)
        self.aviso_cliente = RotuloAviso("aviso")
        self.aviso_numero = RotuloAviso("aviso")
        self.numero.textChanged.connect(self._avisar_numero)
        registrado = QLabel(self.pedido.vendedor or "—", objectName="vendedor")
        registrado.setToolTip("Preenchido sozinho com o nome do usuário do Windows de quem "
                              "cadastrou o pedido")
        for col, texto in enumerate(["Data do pedido", "Cliente", "Nº do pedido",
                                     "Registrado por"]):
            grade.addWidget(QLabel(texto, objectName="rotulo"), 0, col)
        grade.addWidget(self.data, 1, 0)
        grade.addWidget(self.cliente, 1, 1)
        grade.addWidget(self.numero, 1, 2)
        grade.addWidget(registrado, 1, 3)
        grade.addWidget(self.aviso_cliente, 2, 1)
        grade.addWidget(self.aviso_numero, 2, 2)
        grade.setColumnStretch(1, 1)
        geral.addWidget(caixa)

        # Faixa 2: itens
        caixa_itens = QGroupBox("ITENS")
        vi = QVBoxLayout(caixa_itens)
        self.grade_itens = QGridLayout()
        self.grade_itens.setHorizontalSpacing(8)
        self.grade_itens.setVerticalSpacing(8)
        for col, texto in enumerate(LinhaItem.COLUNAS):
            rotulo = QLabel(texto, objectName="cabecalho_itens")
            rotulo.setWordWrap(True)
            self.grade_itens.addWidget(rotulo, 0, col)
        self.grade_itens.setColumnStretch(12, 1)  # Observações
        conteudo = QWidget(objectName="rolagem")
        vc = QVBoxLayout(conteudo)
        vc.setContentsMargins(0, 0, 0, 0)
        vc.addLayout(self.grade_itens)
        vc.addStretch()
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setWidget(conteudo)
        vi.addWidget(rolagem)
        botoes_itens = QHBoxLayout()
        mais = botao("Mais um item", "add")
        mais.setToolTip("Acrescentar uma linha vazia")
        mais.clicked.connect(lambda: self.adicionar_item())
        copiar = botao("Copiar item de cima", "content_copy")
        copiar.setToolTip("Nova linha igual à última (tipo, medidas, prazo e preço); "
                          "só muda o que for diferente")
        copiar.clicked.connect(self.copiar_ultimo)
        botoes_itens.addWidget(mais)
        botoes_itens.addWidget(copiar)
        botoes_itens.addStretch()
        vi.addLayout(botoes_itens)
        geral.addWidget(caixa_itens, 1)

        # Rodapé: avisos e botões
        self.erros = RotuloAviso("erro")
        geral.addWidget(self.erros)
        rodape = QHBoxLayout()
        rodape.addStretch()
        cancelar = botao("Cancelar", "close")
        cancelar.clicked.connect(self.reject)
        salvar = botao("SALVAR PEDIDO", "save", objeto="acao")
        salvar.clicked.connect(self.salvar)
        rodape.addWidget(cancelar)
        rodape.addWidget(salvar)
        geral.addLayout(rodape)

        if novo:
            self.data.definir(datetime.date.today())
            self.adicionar_item()
        else:
            self.data.definir(self.pedido.data)
            self.cliente.setText(self.pedido.cliente)
            self.numero.setText(self.pedido.numero)
            for item in self.pedido.itens:
                self.adicionar_item(item)

    # -------------------------------------------------------------- itens
    def adicionar_item(self, item: Item | None = None) -> LinhaItem:
        linha = LinhaItem(ao_mudar=self._recalcular, ao_remover=self.remover_item)
        if item:
            linha.preencher(item)
        self.linhas.append(linha)
        self._remontar()
        linha.atualizar_falta()
        if item is None:
            linha.codigo.setFocus()
        return linha

    def copiar_ultimo(self) -> None:
        if not self.linhas:
            self.adicionar_item()
            return
        modelo, _ = self.linhas[-1].ler()
        modelo.codigo = ""
        modelo.entrega1 = modelo.entrega2 = None
        modelo.quantidade = None
        modelo.observacoes = ""
        nova = self.adicionar_item(modelo)
        nova.codigo.setFocus()

    def remover_item(self, linha: LinhaItem) -> None:
        if len(self.linhas) == 1:
            self.erros.mostrar("O pedido precisa de pelo menos um item.")
            return
        self.linhas.remove(linha)
        for w in linha.widgets():
            w.deleteLater()
        self._remontar()

    def _remontar(self) -> None:
        for n, linha in enumerate(self.linhas, start=1):
            linha.numero.setText(f"{n}.")
            for col, w in enumerate(linha.widgets()):
                self.grade_itens.addWidget(w, n, col)

    def _recalcular(self) -> None:
        for linha in self.linhas:
            linha.atualizar_falta()

    # -------------------------------------------------------------- avisos
    def _avisar_cliente(self) -> None:
        self.aviso_cliente.mostrar(texto_aviso_cliente(self.cliente))

    def _avisar_numero(self) -> None:
        numero = self.numero.text().strip()
        if numero and self.repo.numero_em_uso(numero, ignorar_id=self.pedido.id):
            self.aviso_numero.mostrar(f"Já existe um pedido nº {numero}.")
        else:
            self.aviso_numero.mostrar("")

    # -------------------------------------------------------------- salvar
    def ler_pedido(self) -> tuple[Pedido, list[str]]:
        avisos = []
        try:
            data = self.data.data()
        except ValueError:
            data = None
            avisos.append("Data do pedido inválida (use dd/mm/aaaa).")
        itens = []
        for n, linha in enumerate(self.linhas, start=1):
            item, invalidos = linha.ler()
            if invalidos:
                avisos.append(f"Item {n}: número inválido em {', '.join(invalidos)}.")
            itens.append(item)
        pedido = Pedido(data=data, cliente=self.cliente.nome(), numero=self.numero.text().strip(),
                        vendedor=self.pedido.vendedor, itens=itens, id=self.pedido.id)
        problemas = [p for p in problemas_do_pedido(pedido)
                     if not (p.startswith("Falta a data") and avisos)]
        return pedido, avisos + problemas

    def salvar(self) -> None:
        pedido, avisos = self.ler_pedido()
        if avisos:
            self.erros.mostrar("\n".join(avisos))
            return
        self.erros.mostrar("")
        existente = self.cliente.existente()
        if existente:
            pedido.cliente = existente
        elif not self._confirmar_cliente_novo(pedido.cliente):
            self.cliente.setFocus()
            self.cliente.mostrar_sugestoes()
            return
        pedido.cliente = self.repo.adicionar_cliente(pedido.cliente)
        self.repo.salvar_pedido(pedido, quem=self.quem)
        self.pedido = pedido
        self.accept()

    def _confirmar_cliente_novo(self, nome: str) -> bool:
        return confirmar_cliente_novo(self, nome)


# --------------------------------------------------------------------------- aba (lista)
class AbaPedidos(QWidget):
    """Lista de todos os pedidos, com pesquisa; clicar na linha abre o pedido."""

    mudou = Signal()
    COLUNAS = ["Data", "Nº pedido", "Cliente", "Itens", "Quantidade (kg)", "Falta (kg)",
               "Próximo prazo", "Registrado por"]

    def __init__(self, repo: Repositorio, vendedor: str, parent=None) -> None:
        super().__init__(parent)
        self.repo = repo
        self.vendedor = vendedor
        self.pedidos: list[Pedido] = []

        geral = QVBoxLayout(self)
        geral.setContentsMargins(14, 14, 14, 14)
        topo = QHBoxLayout()
        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText("Pesquisar por cliente, nº do pedido, código ou medida")
        self.pesquisa.setClearButtonEnabled(True)
        lupa = self.pesquisa.addAction(QIcon(), QLineEdit.LeadingPosition)
        por_icone(lupa, "search", "dica", CORES)
        self.pesquisa.textChanged.connect(self.preencher)
        self.novo = botao("Novo pedido", "add", objeto="acao")
        self.novo.clicked.connect(self.novo_pedido)
        self.atualizar = botao("Atualizar", "refresh")
        self.atualizar.setToolTip("Buscar no banco os pedidos que os colegas lançaram "
                                  "ou mudaram agora")
        self.atualizar.clicked.connect(self.recarregar)
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
        cab.setSectionResizeMode(3, QHeaderView.Stretch)
        # Clique (não mudança de seleção): abre sempre, mesmo já selecionado.
        self.tabela.cellClicked.connect(lambda linha, _c: self.abrir(linha))
        geral.addWidget(self.tabela)
        self.vazio = QLabel("Nenhum pedido ainda. Clique em \"Novo pedido\" para começar.",
                            objectName="dica")
        self.vazio.setAlignment(Qt.AlignCenter)
        geral.addWidget(self.vazio)
        self.recarregar()

    def recarregar(self) -> None:
        self.pedidos = self.repo.pedidos()
        self.preencher()

    def _combina(self, pedido: Pedido, procurado: str) -> bool:
        partes = [pedido.cliente, pedido.numero, pedido.vendedor]
        for i in pedido.itens:
            partes += [i.codigo, descricao(i)]
        return procurado in chave(" ".join(partes))

    def preencher(self) -> None:
        procurado = chave(self.pesquisa.text())
        visiveis = [p for p in self.pedidos if self._combina(p, procurado)]
        self.visiveis = visiveis
        self.tabela.setRowCount(len(visiveis))
        for linha, p in enumerate(visiveis):
            entregue = all(item_entregue(i) for i in p.itens) and bool(p.itens)
            prazo = prazo_mais_proximo(p)
            itens = "; ".join(descricao(i) for i in p.itens)
            textos = [data_tela(p.data), p.numero, p.cliente, itens,
                      kg(sum(i.quantidade or 0 for i in p.itens)),
                      "entregue" if entregue else kg(falta_total(p)),
                      data_tela(prazo) if prazo else ("—" if entregue else ""),
                      p.vendedor]
            for col, texto in enumerate(textos):
                celula = QTableWidgetItem(texto)
                if col in (4, 5):
                    celula.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if col == 3:
                    celula.setToolTip("\n".join(
                        f"{i.codigo}  {descricao(i)}  ·  {kg(i.quantidade)} kg  ·  "
                        f"{dinheiro(i.preco_kg)}/kg" for i in p.itens))
                self.tabela.setItem(linha, col, celula)
        self.tabela.setVisible(bool(self.pedidos))
        self.vazio.setVisible(not self.pedidos)

    def novo_pedido(self) -> None:
        janela = JanelaPedido(self.repo, self.vendedor, parent=self)
        janela.showMaximized()
        if janela.exec():
            self.recarregar()
            self.mudou.emit()

    def abrir(self, linha: int) -> None:
        self.abrir_id(self.visiveis[linha].id)

    def abrir_id(self, pedido_id: int) -> None:
        """Abre o pedido pelo número interno (usado também pela Agenda)."""
        pedido = self.repo.pedido(pedido_id)
        if pedido is None:
            return
        janela = JanelaPedido(self.repo, self.vendedor, pedido, parent=self)
        janela.showMaximized()
        if janela.exec():
            self.recarregar()
            self.mudou.emit()
