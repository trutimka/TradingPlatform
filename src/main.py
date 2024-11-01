import sys

from PyQt5.QtWidgets import QApplication

from data_fetcher import DataFetcher
from portfolio_manager import PortfolioManager
from src.main_window import MainWindow
from strategy_manager import StrategyManager


def main():
    api_key = '7T1DU045ZWGL1PN9'

    data_fetcher = DataFetcher(api_key)
    portfolio_manager = PortfolioManager()
    strategy_manager = StrategyManager()

    app = QApplication(sys.argv)
    main_window = MainWindow(data_fetcher, portfolio_manager, strategy_manager)
    main_window.show()
    sys.exit(app.exec_())

    # api_key = '7T1DU045ZWGL1PN9'
    # data_fetcher = DataFetcher(api_key)
    # portfolio_manager = PortfolioManager()
    # strategy_manager = StrategyManager()
    # backtest_report = BacktestReport()
    #
    # portfolio_manager.add_asset('AAPL')
    #
    # strategy_manager.create_strategy('Simple Moving Average', 'SMA', {'period': 20, 'action': 'buy'})
    #
    # strategy_manager.evaluate_strategy('AAPL', data_fetcher)
    #
    # trades = [{'profit': 100}, {'profit': -20}, {'profit': 50}]
    # backtest_report.calculate_performance(trades)
    # backtest_report.generate_report()


if __name__ == "__main__":
    main()
