import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

# Adiciona o diretório raiz ao path do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()