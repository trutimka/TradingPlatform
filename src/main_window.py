import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QTimer
from data_fetcher import DataFetcher
from portfolio_manager import PortfolioManager
from strategy_manager import StrategyManager


class MainWindow(QMainWindow):
    def __init__(self, data_fetcher, portfolio_manager, strategy_manager):
        super().__init__()
        self.data_fetcher = data_fetcher
        self.portfolio_manager = portfolio_manager
        self.strategy_manager = strategy_manager

        self.setWindowTitle("Trading Platform")
        self.setGeometry(200, 200, 1000, 700)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_portfolio_tab(), "Portfolio")
        self.tabs.addTab(self.create_strategy_tab(), "Strategy")
        self.tabs.addTab(self.create_notifications_tab(), "Notifications")

        self.setCentralWidget(self.tabs)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_prices)
        self.timer.start(60000)

    def create_portfolio_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.asset_input = QLineEdit()
        self.asset_input.setPlaceholderText("Enter asset symbol (e.g., AAPL)")
        add_asset_button = QPushButton("Add Asset")
        add_asset_button.clicked.connect(self.add_asset)

        input_layout.addWidget(self.asset_input)
        input_layout.addWidget(add_asset_button)

        self.asset_table = QTableWidget()
        self.asset_table.setColumnCount(3)
        self.asset_table.setHorizontalHeaderLabels(["Asset", "Current Price", "Actions"])

        layout.addLayout(input_layout)
        layout.addWidget(self.asset_table)

        remove_asset_button = QPushButton("Remove Selected Asset")
        remove_asset_button.clicked.connect(self.remove_selected_asset)
        layout.addWidget(remove_asset_button)

        tab.setLayout(layout)
        return tab

    def create_strategy_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.strategy_name_input = QLineEdit()
        self.strategy_name_input.setPlaceholderText("Enter strategy name")
        self.strategy_params_input = QLineEdit()
        self.strategy_params_input.setPlaceholderText("Enter parameters (comma separated)")

        add_strategy_button = QPushButton("Add Strategy")
        add_strategy_button.clicked.connect(self.add_strategy)

        self.strategy_table = QTableWidget()
        self.strategy_table.setColumnCount(2)
        self.strategy_table.setHorizontalHeaderLabels(["Strategy Name", "Parameters"])

        layout.addWidget(self.strategy_name_input)
        layout.addWidget(self.strategy_params_input)
        layout.addWidget(add_strategy_button)
        layout.addWidget(self.strategy_table)

        remove_strategy_button = QPushButton("Remove Selected Strategy")
        remove_strategy_button.clicked.connect(self.remove_selected_strategy)
        layout.addWidget(remove_strategy_button)

        tab.setLayout(layout)
        return tab

    def create_notifications_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Market change notifications"))
        layout.addWidget(QPushButton("Configure Notifications"))
        tab.setLayout(layout)
        return tab

    def add_asset(self):
        asset_symbol = self.asset_input.text().strip().upper()
        if asset_symbol:
            self.portfolio_manager.add_asset(asset_symbol)
            self.update_asset_table()
            self.fetch_realtime_data(asset_symbol)

    def remove_selected_asset(self):
        selected_row = self.asset_table.currentRow()
        if selected_row >= 0:
            asset_symbol = self.asset_table.item(selected_row, 0).text()
            self.portfolio_manager.remove_asset(asset_symbol)
            self.update_asset_table()

    def add_strategy(self):
        strategy_name = self.strategy_name_input.text().strip()
        strategy_params = self.strategy_params_input.text().strip()

        if strategy_name and strategy_params:
            self.strategy_manager.add_strategy(strategy_name, strategy_params)
            self.update_strategy_table()
            self.strategy_name_input.clear()
            self.strategy_params_input.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Please provide both strategy name and parameters.")

    def remove_selected_strategy(self):
        selected_row = self.strategy_table.currentRow()
        if selected_row >= 0:
            strategy_name = self.strategy_table.item(selected_row, 0).text()
            self.strategy_manager.remove_strategy(strategy_name)
            self.update_strategy_table()

    def fetch_realtime_data(self, asset):
        price = self.data_fetcher.fetch_realtime_data(asset)["Global Quote"]["05. price"]
        # Вот здесь все еще костыль
        if price is not None:
            self.portfolio_manager.assets[asset] = price
            self.update_asset_table()
        else:
            print(f"Could not fetch price for {asset}")

    def update_prices(self):
        for asset in self.portfolio_manager.assets.keys():
            self.fetch_realtime_data(asset)

    def update_asset_table(self):
        self.asset_table.setRowCount(len(self.portfolio_manager.assets))
        for row, (asset, price) in enumerate(self.portfolio_manager.get_assets()):
            self.asset_table.setItem(row, 0, QTableWidgetItem(asset))
            self.asset_table.setItem(row, 1, QTableWidgetItem(str(price) if price is not None else "Fetching..."))
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda checked, asset=asset: self.remove_asset(asset))
            self.asset_table.setCellWidget(row, 2, remove_button)

    def update_strategy_table(self):
        self.strategy_table.setRowCount(len(self.strategy_manager.strategies))
        for row, strategy in enumerate(self.strategy_manager.get_strategies()):
            self.strategy_table.setItem(row, 0, QTableWidgetItem(strategy.name))
            self.strategy_table.setItem(row, 1, QTableWidgetItem(strategy.parameters))

    def remove_asset(self, asset):
        self.portfolio_manager.remove_asset(asset)
        self.update_asset_table()

