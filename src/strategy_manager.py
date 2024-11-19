from src.strategy import Strategy


class StrategyManager:
    def __init__(self, data_fetcher):
        self.strategies = []
        self.data_fetcher = data_fetcher

    def add_strategy(self, asset, strategy, parameters):
        new_strategy = Strategy(asset, strategy, parameters)
        self.strategies.append(new_strategy)
        return self.execute_strategy(new_strategy)

    def get_strategies(self):
        return self.strategies

    def remove_strategy(self, index):
        if 0 <= index < len(self.strategies):
            del self.strategies[index]
        else:
            raise IndexError("Invalid strategy index.")

    def execute_strategy(self, strategy):
        asset, strategy_name, parameters = strategy.asset, strategy.strategy_name, strategy.parameters
        interval = parameters.get("Interval", "daily")
        interval = self.convert_interval(interval)
        print(parameters)
        if strategy_name == "SMA":
            fast_period = int(parameters["Fast Period:"])
            slow_period = int(parameters["Slow Period:"])
            return self.execute_sma(asset, fast_period=fast_period, slow_period=slow_period, interval=interval)
        elif strategy_name == "RSI":
            time_period = int(parameters["Time Period:"])
            threshold = int(parameters["Threshold:"])
            return self.execute_rsi_threshold(asset, threshold=threshold, interval=interval, time_period=time_period)
        elif strategy_name == "BBands":
            dev_multiplier = int(parameters["Multiplier:"])
            time_period = int(parameters["Time Period:"])
            return self.execute_bollinger_bands(asset, interval=interval, time_period=time_period,
                                                dev_multiplier=dev_multiplier)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

    def convert_interval(self, interval):
        return interval.lower().replace(" ", "")

    def execute_rsi_threshold(self, symbol, threshold=70, interval='daily', time_period=14):
        """
        Выполняет стратегию на основе RSI:
        - "SELL", если RSI выше заданного порога.
        - "BUY", если RSI ниже заданного порога (обычно 30).
        """
        rsi_data = self.data_fetcher.fetch_rsi(symbol, interval, time_period)
        if not rsi_data:
            return "API error"

        last_date = sorted(rsi_data.keys())[-1]
        rsi_value = float(rsi_data[last_date]['RSI'])

        if rsi_value > threshold:
            return "SELL"
        elif rsi_value < 100 - threshold:
            return "BUY"
        return "HOLD"

    def execute_sma(self, symbol, fast_period=14, slow_period=50, interval='daily'):
        """
        Выполняет стратегию SMA Crossover:
        Сигнал "BUY", если SMA(fast_period) пересекает SMA(slow_period) снизу вверх.
        Сигнал "SELL", если SMA(fast_period) пересекает SMA(slow_period) сверху вниз.
        """
        fast_sma = self.data_fetcher.fetch_sma(symbol, interval, fast_period)
        slow_sma = self.data_fetcher.fetch_sma(symbol, interval, slow_period)

        if not fast_sma or not slow_sma:
            return "API error"

        fast_sma = {date: float(data['SMA']) for date, data in fast_sma.items()}
        slow_sma = {date: float(data['SMA']) for date, data in slow_sma.items()}

        fast_dates = sorted(fast_sma.keys())[-2:]
        slow_dates = sorted(slow_sma.keys())[-2:]

        if len(fast_dates) < 2 or len(slow_dates) < 2:
            return "Not enough data."

        fast_prev, fast_curr = fast_sma[fast_dates[0]], fast_sma[fast_dates[1]]
        slow_prev, slow_curr = slow_sma[slow_dates[0]], slow_sma[slow_dates[1]]

        if fast_prev <= slow_prev and fast_curr > slow_curr:
            return "BUY"
        elif fast_prev >= slow_prev and fast_curr < slow_curr:
            return "SELL"
        return "HOLD"

    def execute_bollinger_bands(self, symbol, interval='daily', time_period=14, dev_multiplier=2):
        """
        Выполняет стратегию Bollinger Bands:
        - "BUY", если цена закрытия ниже нижней полосы.
        - "SELL", если цена закрытия выше верхней полосы.
        """
        bollinger_data = self.data_fetcher.fetch_bollinger_bands(symbol, interval, time_period)
        if not bollinger_data:
            return "API error."

        last_date = sorted(bollinger_data.keys())[-1]
        bands = bollinger_data[last_date]

        middle_band = float(bands['Real Middle Band'])
        upper_band = float(bands['Real Upper Band'])
        lower_band = float(bands['Real Lower Band'])

        std_dev = (upper_band - middle_band)
        adjusted_upper_band = middle_band + dev_multiplier * std_dev
        adjusted_lower_band = middle_band - dev_multiplier * std_dev

        close_price = float(bands['Real Middle Band'])

        if close_price < adjusted_lower_band:
            return "BUY"
        elif close_price > adjusted_upper_band:
            return "SELL"

        return "HOLD"
