import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow


def main():
    api_key = 'DNBLDKXI1A4BDSQC'
    app = QApplication(sys.argv)
    main_window = MainWindow(api_key)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
