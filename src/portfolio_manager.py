class PortfolioManager:
    def __init__(self):
        self.assets = {}

    def add_asset(self, asset):
        if asset not in self.assets:
            self.assets[asset] = None

    def remove_asset(self, asset):
        if asset in self.assets:
            del self.assets[asset]

    def get_assets(self):
        return self.assets.items()