import sqlite3


class Database:
    connection = None
    cursor = None
    db_name = "../assets/trading_platform.db"

    @staticmethod
    def connect():
        Database.connection = sqlite3.connect(Database.db_name)
        Database.connection.row_factory = sqlite3.Row
        Database.cursor = Database.connection.cursor()
        Database.create_tables()

    @staticmethod
    def create_tables():
        Database.cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            current_price REAL
        )
        ''')

        Database.cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            asset_id INTEGER,
            indicator TEXT,
            condition TEXT,
            FOREIGN KEY (asset_id) REFERENCES assets(id)
        )
        ''')

        Database.cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_name TEXT NOT NULL,
            activation_price REAL NOT NULL
        )
        ''')
        Database.connection.commit()

    @staticmethod
    def close():
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.close()
        Database.connection.close()
        Database.connection = None
        Database.cursor = None

    @staticmethod
    def get_assets():
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.execute("SELECT * FROM assets")
        return Database.cursor.fetchall()

    @staticmethod
    def add_asset(name, current_price):
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.execute("INSERT OR REPLACE INTO assets (name, current_price) VALUES (?, ?)",
                                (name, current_price))
        Database.connection.commit()
        return Database.cursor.lastrowid

    @staticmethod
    def update_asset(asset, new_price):
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.execute("UPDATE assets SET current_price = ? WHERE name = ?", (new_price, asset))
        Database.connection.commit()

    @staticmethod
    def remove_asset(asset):
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.execute("DELETE FROM assets WHERE name = ?", (asset,))
        Database.connection.commit()

    @staticmethod
    def remove_all_assets():
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.execute("DELETE FROM assets")
        Database.connection.commit()

    @staticmethod
    def get_notifications():
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.execute("SELECT * FROM notifications")
        return Database.cursor.fetchall()

    @staticmethod
    def get_notifications_for_asset(asset):
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.execute("SELECT * FROM notifications WHERE asset_name = ?", (asset,))
        return Database.cursor.fetchall()

    @staticmethod
    def add_notification(asset_name, activation_price):
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.execute(
            "INSERT INTO notifications (asset_name, activation_price) VALUES (?, ?)",
            (asset_name, activation_price)
        )
        Database.connection.commit()
        return Database.cursor.lastrowid

    @staticmethod
    def remove_notification(notification_id):
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
        Database.connection.commit()

    @staticmethod
    def clear_notifications():
        if Database.cursor is None:
            raise Exception("Database not connected.")
        Database.cursor.execute("DELETE FROM notifications")
        Database.connection.commit()

    # @staticmethod
    # def add_strategy(name, asset_id, indicator, condition):
    #     Database.cursor.execute(
    #         "INSERT INTO strategies (name, asset_id, indicator, condition) VALUES (?, ?, ?, ?)",
    #         (name, asset_id, indicator, condition)
    #     )
    #     Database.connection.commit()
    #     return Database.cursor.lastrowid
    #
    # @staticmethod
    # def get_strategies():
    #     Database.cursor.execute("SELECT * FROM strategies")
    #     return Database.cursor.fetchall()
    #
    # @staticmethod
    # def delete_strategy(strategy_id):
    #     Database.cursor.execute("DELETE FROM strategies WHERE id = ?", (strategy_id,))
    #     Database.connection.commit()

