from database import Database


class PortfolioManager:
    def __init__(self):
        Database.connect()
        self.assets = self.load_assets_from_db()

    def load_assets_from_db(self):
        return {asset[1]: asset[2] for asset in Database.get_assets()}

    def add_asset(self, asset, price=None):
        if asset not in self.assets:
            Database.add_asset(asset, price)
            self.assets[asset] = price

    def update_asset(self, asset, new_price):
        if asset in self.assets:
            Database.update_asset(asset, new_price)
            self.assets[asset] = new_price

    def remove_asset(self, asset):
        if asset in self.assets:
            Database.remove_asset(asset)
            del self.assets[asset]

    def remove_all_assets(self):
        Database.remove_all_assets()
        self.assets.clear()

    def get_assets(self):
        return self.assets.items()
