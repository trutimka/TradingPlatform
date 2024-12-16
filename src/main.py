import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from dotenv import load_dotenv
import os


def main():
    load_dotenv()
    api_key = os.getenv('API_KEY')
    app = QApplication(sys.argv)
    main_window = MainWindow(api_key)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
