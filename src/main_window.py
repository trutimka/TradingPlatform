import sys
import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QHBoxLayout, QMessageBox, QComboBox, QFormLayout,
    QPlainTextEdit
)
from PyQt5.QtCore import QTimer
from data_fetcher import DataFetcher
from portfolio_manager import PortfolioManager
from strategy_manager import StrategyManager
from database import Database
import plotly.graph_objs as go


class MainWindow(QMainWindow):
    def __init__(self, api_key):
        super().__init__()
        self.data_fetcher = DataFetcher(api_key)
        self.portfolio_manager = PortfolioManager()
        self.strategy_manager = StrategyManager()
        Database.connect()

        self.setWindowTitle("Trading Platform")
        self.setGeometry(200, 200, 1000, 700)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_portfolio_tab(), "Portfolio")
        self.tabs.addTab(self.create_strategy_tab(), "Strategy")
        self.tabs.addTab(self.create_notifications_tab(), "Notifications")
        self.tabs.addTab(self.create_charts_tab(), "Charts")

        self.setCentralWidget(self.tabs)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_prices)
        self.timer.start(60000)

        self.update_prices()
        self.update_asset_table()
        self.update_notification_table()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to close the application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

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

        layout.addWidget(QLabel("Select an Asset"))
        self.asset_selector = QComboBox()
        print(self.portfolio_manager.get_assets())
        self.asset_selector.addItems([assets[0] for assets in self.portfolio_manager.get_assets()])
        layout.addWidget(self.asset_selector)

        layout.addWidget(QLabel("Select a Strategy"))
        self.strategy_selector = QComboBox()
        self.strategy_selector.addItems([
            "Select a Strategy",
            "Moving Average",
            "Breakout Strategy",
            "Mean Reversion Strategy"
        ])
        self.strategy_selector.currentIndexChanged.connect(self.update_strategy_params)
        layout.addWidget(self.strategy_selector)

        self.period_selector = QComboBox()
        self.period_selector.addItems(["Select Period", "Daily", "Weekly", "Monthly"])
        self.period_selector.hide()
        layout.addWidget(self.period_selector)

        self.param_form_layout = QFormLayout()
        layout.addLayout(self.param_form_layout)

        self.strategy_info = QLabel("Strategy info will be displayed here.")
        layout.addWidget(self.strategy_info)

        apply_strategy_button = QPushButton("Apply Strategy")
        apply_strategy_button.clicked.connect(self.apply_strategy)
        layout.addWidget(apply_strategy_button)

        tab.setLayout(layout)
        return tab

    def update_strategy_params(self):
        for i in reversed(range(self.param_form_layout.count())):
            self.param_form_layout.itemAt(i).widget().deleteLater()

        selected_strategy = self.strategy_selector.currentText()
        if selected_strategy == "Moving Average":
            self.period_selector.show()
            self.add_parameter_field("Moving Average Period:", QLineEdit())
            sma_type = QComboBox()
            sma_type.addItems(["SMA", "EMA"])
            self.add_parameter_field("Moving Average Type:", sma_type)
        elif selected_strategy == "Breakout Strategy":
            self.period_selector.hide()
            self.add_parameter_field("Breakout Level:", QLineEdit())
            breakout_direction = QComboBox()
            breakout_direction.addItems(["buy", "sell"])
            self.add_parameter_field("Direction (buy/sell):", breakout_direction)
        elif selected_strategy == "Mean Reversion Strategy":
            self.period_selector.show()
            self.add_parameter_field("Calculation Period:", QLineEdit())
            self.add_parameter_field("Allowable Deviation:", QLineEdit())
        else:
            self.period_selector.hide()

        self.update_strategy_info(selected_strategy)

    def update_strategy_info(self, strategy_name):
        info_text = {
            "Moving Average": "Moving Average strategy uses SMA or EMA for trend analysis.",
            "Breakout Strategy": "Breakout Strategy aims to capitalize on strong price movements.",
            "Mean Reversion Strategy": "Mean Reversion Strategy trades on the price's tendency to return to mean.",
        }
        self.strategy_info.setText(info_text.get(strategy_name, "Select a strategy to see details."))

    def add_parameter_field(self, label_text, widget):
        """Helper method to add a labeled input field to the form layout."""
        self.param_form_layout.addRow(label_text, widget)

    def apply_strategy(self):
        selected_asset = self.asset_selector.currentText()
        selected_strategy = self.strategy_selector.currentText()

        if selected_strategy == "Select a Strategy" or selected_asset == "":
            QtWidgets.QMessageBox.warning(self, "Error", "Please select both an asset and a strategy.")
            return

        parameters = {}
        for i in range(self.param_form_layout.count()):
            label_item = self.param_form_layout.itemAt(i, QFormLayout.LabelRole)
            field_item = self.param_form_layout.itemAt(i, QFormLayout.FieldRole)

            if label_item and field_item:
                label = label_item.widget().text() if label_item.widget() else None
                input_widget = field_item.widget()
                if isinstance(input_widget, QLineEdit):
                    parameters[label] = input_widget.text() if label else ""
                elif isinstance(input_widget, QComboBox):
                    parameters[label] = input_widget.currentText() if label else ""

        if self.period_selector.isVisible() and self.period_selector.currentText() != "Select Period":
            parameters["Period"] = self.period_selector.currentText()

        QtWidgets.QMessageBox.information(
            self, "Strategy Applied",
            f"Strategy '{selected_strategy}' applied to {selected_asset} with parameters: {parameters}"
        )

    def create_notifications_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.notification_asset_input = QLineEdit()
        self.notification_asset_input.setPlaceholderText("Enter asset symbol for notification")
        self.price_threshold_input = QLineEdit()
        self.price_threshold_input.setPlaceholderText("Enter price threshold")

        add_notification_button = QPushButton("Add Notification")
        add_notification_button.clicked.connect(self.add_notification)

        self.notification_table = QTableWidget()
        self.notification_table.setColumnCount(3)
        self.notification_table.setHorizontalHeaderLabels(["Asset", "Price Threshold", "Remove"])

        layout.addWidget(QLabel("Market change notifications"))
        layout.addWidget(self.notification_asset_input)
        layout.addWidget(self.price_threshold_input)
        layout.addWidget(add_notification_button)
        layout.addWidget(self.notification_table)

        tab.setLayout(layout)
        return tab

    def create_charts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.chart_combo = QComboBox()
        self.chart_combo.addItem("")
        self.chart_combo.addItems(self.portfolio_manager.assets.keys())
        self.chart_combo.setCurrentIndex(0)
        self.chart_combo.currentIndexChanged.connect(self.update_chart)

        self.interval_combo = QComboBox()
        self.interval_combo.addItems(['1min', '5min', '15min', '30min', '60min'])
        self.interval_combo.setCurrentIndex(1)
        self.interval_combo.currentIndexChanged.connect(self.update_chart)

        layout.addWidget(self.chart_combo)
        layout.addWidget(self.interval_combo)

        self.chart_browser = QtWebEngineWidgets.QWebEngineView(self)
        layout.addWidget(self.chart_browser)

        tab.setLayout(layout)
        return tab

    def add_asset(self):
        asset_symbol = self.asset_input.text().strip().upper()
        if asset_symbol:
            price = self.fetch_realtime_data(asset_symbol)
            self.portfolio_manager.add_asset(asset_symbol, price)
            self.update_asset_table()
            self.asset_input.clear()
            self.update_asset_selector()

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

    def add_notification(self):
        asset = self.notification_asset_input.text().strip().upper()
        try:
            threshold = float(self.price_threshold_input.text().strip())
            if asset and threshold > 0:
                Database.add_notification(asset, threshold)
                self.update_notification_table()
                self.notification_asset_input.clear()
                self.price_threshold_input.clear()
            else:
                QMessageBox.warning(self, "Invalid Input", "Please provide a valid asset and threshold.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid price threshold.")

    def update_notification_table(self):
        notifications = {row[0]: [row[1], row[2]] for row in Database.get_notifications()}

        self.notification_table.setRowCount(len(notifications))
        for row, (notification_id, notification_data) in enumerate(notifications.items()):
            threshold = notification_data[1]
            asset = notification_data[0]
            self.notification_table.setItem(row, 0, QTableWidgetItem(asset))
            self.notification_table.setItem(row, 1, QTableWidgetItem(str(threshold)))
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda checked, notif_id=notification_id: self.remove_notification(notif_id))
            self.notification_table.setCellWidget(row, 2, remove_button)

    def remove_notification(self, not_id):
        Database.remove_notification(not_id)
        self.update_notification_table()

    def fetch_realtime_data(self, asset):
        price = self.data_fetcher.fetch_realtime_data(asset)["Global Quote"]["05. price"]
        # Вот здесь все еще костыль
        if price is not None:
            self.portfolio_manager.add_asset(asset, price)
            return price
        else:
            print(f"Could not fetch price for {asset}")

    def update_prices(self):
        for asset in self.portfolio_manager.assets.keys():
            price = self.fetch_realtime_data(asset)
            notifications = {row[0]: [row[1], row[2]] for row in Database.get_notifications_for_asset(asset)}
            for row, (notification_id, notification_data) in enumerate(notifications.items()):
                threshold = notification_data[1]
                if float(price) >= threshold:
                    self.show_notification(asset, price)

    def show_notification(self, asset, price):
        try:
            QMessageBox.information(self, "Price Alert", f"{asset} has reached the price of {price}!")
        except WindowsError:
            QMessageBox.warning(self, "Invalid Notification", "Something wrong with notifications.")

    def update_asset_table(self):
        self.portfolio_manager.load_assets_from_db()
        self.asset_table.setRowCount(len(self.portfolio_manager.assets))
        for row, (asset, price) in enumerate(self.portfolio_manager.get_assets()):
            self.asset_table.setItem(row, 0, QTableWidgetItem(asset))
            self.asset_table.setItem(row, 1, QTableWidgetItem(str(price) if price is not None else "Fetching..."))
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda checked, asset=asset: self.remove_asset(asset))
            self.asset_table.setCellWidget(row, 2, remove_button)

    def remove_asset(self, asset):
        self.portfolio_manager.remove_asset(asset)
        self.update_asset_table()

    def update_strategy_table(self):
        self.strategy_table.setRowCount(len(self.strategy_manager.strategies))
        for row, strategy in enumerate(self.strategy_manager.get_strategies()):
            self.strategy_table.setItem(row, 0, QTableWidgetItem(strategy.name))
            self.strategy_table.setItem(row, 1, QTableWidgetItem(strategy.parameters))

    def update_chart(self):
        asset_symbol = self.chart_combo.currentText()
        if asset_symbol == "":
            return
        data = self.data_fetcher.fetch_historical_data(asset_symbol, interval=self.interval_combo.currentText())
        time_series = data[f'Time Series ({self.interval_combo.currentText()})']
        df = pd.DataFrame({
            "Date": pd.to_datetime(list(time_series.keys())),
            "Open": [float(values['1. open']) for values in time_series.values()],
            "High": [float(values['2. high']) for values in time_series.values()],
            "Low": [float(values['3. low']) for values in time_series.values()],
            "Close": [float(values['4. close']) for values in time_series.values()]
        })

        df = df.sort_values(by="Date")
        fig = go.Figure(data=[go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])

        fig.update_layout(
            title=f"{data['Meta Data']['2. Symbol']} Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            template="plotly_dark"
        )

        self.chart_browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

    def update_asset_selector(self):
        self.asset_selector.clear()
        self.asset_selector.addItems("")
        self.asset_selector.addItems(self.portfolio_manager.assets.keys())
        self.chart_combo.setCurrentIndex(0)

