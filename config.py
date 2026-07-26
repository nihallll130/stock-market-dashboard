from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "stocks.db"
UPLOADS_DIR = BASE_DIR / "uploads"

DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

APP_TITLE = "📈 Stock Market Dashboard"
APP_ICON = "📊"
PAGE_CONFIG = {
    "page_title": "Stock Dashboard",
    "page_icon": APP_ICON,
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

POPULAR_STOCKS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "NVDA",
    "TSLA", "META", "NFLX", "UBER", "AMD",
    "JPM", "BAC", "GS", "WMT", "KO",
]

MA_PERIODS = [20, 50, 200]
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

ALERT_TYPES = ["Price Rise", "Price Drop", "Volume Spike"]
DEFAULT_ALERT_THRESHOLD = 5

COLOR_POSITIVE = "#00CC96"
COLOR_NEGATIVE = "#EF553B"
COLOR_NEUTRAL = "#636EFA"
