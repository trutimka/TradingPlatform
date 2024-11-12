import sys

from PyQt5.QtWidgets import QApplication

from data_fetcher import DataFetcher
from portfolio_manager import PortfolioManager
from src.main_window import MainWindow
from strategy_manager import StrategyManager
from database import Database


def main():
    # api_key = '7T1DU045ZWGL1PN9'
    api_key = 'DNBLDKXI1A4BDSQC'
    app = QApplication(sys.argv)
    main_window = MainWindow(api_key)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


# from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
# import plotly.graph_objs as go
# import pandas as pd
#
#
# class Widget(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.button = QtWidgets.QPushButton('Show Candlestick Chart', self)
#         self.browser = QtWebEngineWidgets.QWebEngineView(self)
#
#         vlayout = QtWidgets.QVBoxLayout(self)
#         vlayout.addWidget(self.button, alignment=QtCore.Qt.AlignHCenter)
#         vlayout.addWidget(self.browser)
#
#         self.button.clicked.connect(self.show_graph)
#         self.resize(1000, 800)
#
#     def show_graph(self):
#         # Здесь подставьте ваши данные, которые вы парсили.
#         # Пример данных для построения свечного графика
#         data = {
#             'Date': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05'],
#             'Open': [100, 105, 103, 110, 108],
#             'High': [105, 107, 106, 112, 111],
#             'Low': [99, 102, 101, 107, 106],
#             'Close': [104, 106, 105, 111, 109]
#         }
#
#         df = pd.DataFrame(data)
#         df['Date'] = pd.to_datetime(df['Date'])
#
#         # Построение графика
#         fig = go.Figure(data=[go.Candlestick(
#             x=df['Date'],
#             open=df['Open'],
#             high=df['High'],
#             low=df['Low'],
#             close=df['Close']
#         )])
#
#         fig.update_layout(
#             title="Candlestick Chart",
#             xaxis_title="Date",
#             yaxis_title="Price",
#             xaxis_rangeslider_visible=False,
#             template="plotly_dark",
#         )
#
#         # Отображение графика в браузере
#         self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
#
#
# if __name__ == "__main__":
#     app = QtWidgets.QApplication([])
#     widget = Widget()
#     widget.show()
#     app.exec()

