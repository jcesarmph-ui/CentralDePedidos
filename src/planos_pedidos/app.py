"""Ponto de entrada: abre a janela maximizada."""

import sys

from PySide6.QtWidgets import QApplication

from planos_pedidos.interface.janela import JanelaPrincipal


def main() -> int:
    if sys.platform == "win32":  # barra de tarefas com o ícone do programa, não o do Python
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CentralDePedidos")
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.showMaximized()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
