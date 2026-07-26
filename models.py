import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd

class StockDatabase:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()

    def _get_connection(self):
        return sqlite3.connect(str(self.db_path))

    def init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT UNIQUE NOT NULL,
                company_name TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                quantity REAL NOT NULL,
                purchase_price REAL NOT NULL,
                purchase_date TIMESTAMP NOT NULL,
                transaction_type TEXT DEFAULT 'BUY'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                date TIMESTAMP NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                UNIQUE(ticker, date)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                threshold REAL,
                is_active INTEGER DEFAULT 1,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_to_watchlist(self, ticker: str, company_name: str = None) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO watchlist (ticker, company_name) VALUES (?, ?)",
                (ticker.upper(), company_name or ticker)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_from_watchlist(self, ticker: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker.upper(),))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def get_watchlist(self) -> list:
        conn = self._get_connection()
        df = pd.read_sql_query("SELECT * FROM watchlist ORDER BY added_date DESC", conn)
        conn.close()
        return df.to_dict('records') if len(df) > 0 else []

    def is_in_watchlist(self, ticker: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM watchlist WHERE ticker = ? LIMIT 1", (ticker.upper(),))
        result = cursor.fetchone() is not None
        conn.close()
        return result

    def add_portfolio_transaction(self, ticker: str, quantity: float, price: float, trans_type: str = "BUY"):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO portfolio (ticker, quantity, purchase_price, purchase_date, transaction_type)
               VALUES (?, ?, ?, ?, ?)""",
            (ticker.upper(), quantity, price, datetime.now(), trans_type)
        )
        conn.commit()
        conn.close()

    def get_portfolio(self) -> dict:
        conn = self._get_connection()
        df = pd.read_sql_query("""
            SELECT ticker,
                   SUM(CASE WHEN transaction_type='BUY' THEN quantity ELSE -quantity END) as total_qty,
                   AVG(purchase_price) as avg_cost
            FROM portfolio
            GROUP BY ticker
            HAVING total_qty > 0
        """, conn)
        conn.close()
        return df.to_dict('records') if len(df) > 0 else []

    def save_price_history(self, ticker: str, df: pd.DataFrame):
        conn = self._get_connection()
        df['ticker'] = ticker.upper()
        df['date'] = pd.to_datetime(df.index).strftime('%Y-%m-%d')
        try:
            df.to_sql('price_history', conn, if_exists='append', index=False)
        except ValueError:
            pass
        conn.close()

    def get_price_history(self, ticker: str, limit: int = 100) -> pd.DataFrame:
        conn = self._get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM price_history WHERE ticker = ? ORDER BY date DESC LIMIT ?",
            conn,
            params=(ticker.upper(), limit)
        )
        conn.close()
        return df.iloc[::-1] if len(df) > 0 else pd.DataFrame()

    def add_alert(self, ticker: str, alert_type: str, threshold: float) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO alerts (ticker, alert_type, threshold)
                   VALUES (?, ?, ?)""",
                (ticker.upper(), alert_type, threshold)
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_alerts(self) -> list:
        conn = self._get_connection()
        df = pd.read_sql_query("SELECT * FROM alerts WHERE is_active = 1", conn)
        conn.close()
        return df.to_dict('records') if len(df) > 0 else []

    def remove_alert(self, alert_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE alerts SET is_active = 0 WHERE id = ?", (alert_id,))
        conn.commit()
        conn.close()
