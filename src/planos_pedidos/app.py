"""Ponto de entrada: abre o banco da pasta de dados e a janela maximizada."""

import sys

from PySide6.QtWidgets import QApplication

from planos_pedidos.dados.caminhos import LISTA_CLIENTES, NOME_BANCO, pasta_dados
from planos_pedidos.dados.repositorio import Repositorio
from planos_pedidos.interface.janela import JanelaPrincipal


def main() -> int:
    if sys.platform == "win32":  # barra de tarefas com o ícone do programa, não o do Python
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CentralDePedidos")
    app = QApplication(sys.argv)
    pasta = pasta_dados()
    repo = Repositorio(pasta / NOME_BANCO)
    repo.importar_clientes(pasta / LISTA_CLIENTES)  # lista inicial (só os que faltam)
    janela = JanelaPrincipal(repo)
    janela.showMaximized()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
