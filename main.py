import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
