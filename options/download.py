import logging
from typing import Optional

import yfinance as yf

log = logging.getLogger("options - download")
logging.basicConfig(level=logging.INFO)


def get_ticker(ticker: str) -> Optional[yf.Ticker]:
    """Create a yfinance ticker, logging construction errors and returning None.

    Successful construction alone does not confirm that options data exists.
    """
    try:
        data = yf.Ticker(ticker)
        return data
    except Exception as e:
        log.error(e)
        return None
