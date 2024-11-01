from strategy import Strategy


class StrategyManager:
    def __init__(self):
        self.strategies = []

    def add_strategy(self, name, parameters):
        new_strategy = Strategy(name, parameters)
        self.strategies.append(new_strategy)

    def remove_strategy(self, name):
        self.strategies = [s for s in self.strategies if s.name != name]

    def get_strategies(self):
        return self.strategies
