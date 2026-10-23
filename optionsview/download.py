import logging
import yfinance as yf
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import math



log = logging.getLogger("optionsview - download")
logging.basicConfig(level=logging.INFO)


def get_ticker(ticker: str) -> Optional[yf.Ticker]:
    """Create a yfinance ticker, logging construction errors and returning None.

    Successful construction alone does not confirm that optionsview data exists.
    """
    try:
        data = yf.Ticker(ticker)
        return data
    except Exception as e:
        log.error(e)
        return None


@dataclass
class StockPrice:
    price: float
    as_of: datetime


def get_stock_price(ticker: yf.Ticker) -> Optional[StockPrice]:
    """Return the regular-market price and its timestamp, or None."""
    try:
        info = ticker.get_info()
        price = float(info["regularMarketPrice"])
        as_of = datetime.fromtimestamp(
            info["regularMarketTime"], tz=timezone.utc
        )

        if not math.isfinite(price) or price <= 0:
            raise ValueError(f"Invalid stock price: {price}")

        return StockPrice(price=price, as_of=as_of)

    except Exception as exc:
        log.warning("Unable to retrieve stock price: %s", exc)
        return None