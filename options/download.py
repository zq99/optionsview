import yfinance as yf
import logging

log = logging.getLogger("options - download")
logging.basicConfig(level=logging.INFO)


def get_ticker(ticker):
    try:
        data = yf.Ticker(ticker)
        return data
    except Exception as e:
        log.error(e)
        return None
