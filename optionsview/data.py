import logging
from enum import Enum
from typing import Optional

import numpy as np
import pandas as pd

from optionsview.common import export_df
from optionsview.common import get_file_name
from optionsview.download import (
    get_ticker, get_stock_price, StockPrice
)
from optionsview.headers import __straddle_headers, final_headers
from optionsview.result import (
    Result, __get_result_of_output_files, OptionsViewResult
)

log = logging.getLogger("optionsview - data")
logging.basicConfig(level=logging.INFO)


class View(Enum):
    """Select which optionsview views to export to CSV."""

    STRADDLE = 1
    STACKED = 2
    ALL = 3


stacked_name = 'options_chain'
straddle_name = 'straddle'


def __reformat(
        df: pd.DataFrame,
        option_type: str,
        date: str,
        symbol: str
) -> pd.DataFrame:
    """Insert option type, expiry date and symbol into the supplied DataFrame.

    Modify the DataFrame in place and return the same object.
    """
    df.insert(loc=0, column='option_type', value=option_type)
    df.insert(loc=1, column='expire_date', value=date)
    df.insert(loc=2, column='symbol', value=symbol)
    return df


def __get_options_view_data(
        symbol: str,
) -> Optional[OptionsViewResult]:
    """Fetch optionsview chains and build straddle and stacked DataFrames.

    Match calls and puts by expiry date and strike for the straddle view.
    Stack call and put rows separately for the tabular view. This function
    prepares data in memory; it does not export files.

    Return None for a non-string symbol or a missing ticker.
    """
    if not isinstance(symbol, str):
        log.error("Please enter a symbol for the instrument")
        return None

    # Create the ticker used to retrieve expiry dates and optionsview chains.
    yticker = get_ticker(symbol)
    if yticker is None:
        log.error(f"No data for {symbol} returned from the api")
        return None

    quote: StockPrice = get_stock_price(yticker)
    stock_price = quote.price if quote is not None else None
    stock_price_as_of = quote.as_of.isoformat() if quote is not None else None

    calls_df_list = []
    puts_df_list = []
    straddle_df_list = []

    # Retrieve each available expiry separately.
    expire_dates = yticker.options
    for date in expire_dates:
        log.info(f"{symbol} downloading exercise date {date}")

        options_chain = None
        try:
            options_chain = yticker.option_chain(date)
        except Exception as exc:
            log.error(
                "Error getting optionsview chain data for %s on %s: %s",
                symbol,
                date,
                exc,
            )

        if options_chain is not None:
            calls_df = __reformat(
                df=options_chain.calls, option_type='CALLS', date=date, symbol=symbol
            )
            calls_df_list.append(calls_df)

            puts_df = __reformat(
                df=options_chain.puts, option_type='PUTS', date=date, symbol=symbol
            )
            puts_df_list.append(puts_df)

            # Retain only strikes present in both calls and puts for this expiry.
            straddle_df = pd.DataFrame.merge(
                calls_df, puts_df, on=['expire_date', 'strike'], how='inner',
                suffixes=('_call', '_put'), sort=False
            )

            straddle_df_list.append(straddle_df)

    stacked_all_df = pd.DataFrame()
    straddle_all_df = pd.DataFrame()

    if straddle_df_list:
        straddle_all_df = pd.concat(straddle_df_list, axis=0, ignore_index=True)
        straddle_all_df = straddle_all_df[__straddle_headers]
        straddle_all_df.insert(loc=0, column='symbol', value=symbol)
        straddle_all_df['inTheMoney_call'] = np.where(straddle_all_df['inTheMoney_call'], 'Y', 'N')
        straddle_all_df['inTheMoney_put'] = np.where(straddle_all_df['inTheMoney_put'], 'Y', 'N')
        straddle_all_df.sort_values(by=['expire_date', 'strike'], inplace=True, ascending=[True, True])

    if calls_df_list:
        calls_all_df = pd.concat(calls_df_list, axis=0, ignore_index=True)
        stacked_all_df = pd.concat([stacked_all_df, calls_all_df])

    if puts_df_list:
        puts_all_df = pd.concat(puts_df_list, axis=0, ignore_index=True)
        stacked_all_df = pd.concat([stacked_all_df, puts_all_df])

    if not stacked_all_df.empty:
        stacked_all_df['inTheMoney'] = np.where(stacked_all_df['inTheMoney'], 'Y', 'N')

    for df in [straddle_all_df, stacked_all_df]:
        df.rename(columns=final_headers, inplace=True)

        if "symbol" in df.columns:
            position = df.columns.get_loc("symbol") + 1
            df.insert(position, "stock_price", stock_price)
            df.insert(
                position + 1,
                "stock_price_retrieved_at",
                stock_price_as_of,
            )

    return OptionsViewResult(
        straddle=straddle_all_df,
        stacked=stacked_all_df,
    )


def get_options_view(symbol: str) -> Optional[OptionsViewResult]:
    """Download both views and return them as named attributes."""
    return __get_options_view_data(symbol)


def download_options_view(
        symbol: str,
        view_type: View = View.STRADDLE,
        folder: Optional[str] = None,
) -> Result:
    """Download both views and export the selected view or views to CSV."""
    views = get_options_view(symbol)

    if views is None:
        return Result.get_empty_result()

    if view_type in (View.STRADDLE, View.ALL) and views.straddle.empty:
        return Result.get_empty_result()

    if view_type in (View.STACKED, View.ALL) and views.stacked.empty:
        return Result.get_empty_result()

    file_name_straddle, file_name_stacked = None, None
    exports_succeeded = True

    if view_type in (View.STRADDLE, View.ALL):
        file_name_straddle = get_file_name(
            f"{straddle_name}_{symbol}", True, folder
        )
        succeeded = export_df(
            data_df=views.straddle,
            file_name=file_name_straddle,
            index_required=False,
        )
        exports_succeeded = exports_succeeded and succeeded

    if view_type in (View.STACKED, View.ALL):
        file_name_stacked = get_file_name(
            f"{stacked_name}_{symbol}", True, folder
        )
        succeeded = export_df(
            data_df=views.stacked,
            file_name=file_name_stacked,
            index_required=False,
        )
        exports_succeeded = exports_succeeded and succeeded

    result = __get_result_of_output_files(
        straddle_file_name=file_name_straddle,
        stacked_file_name=file_name_stacked,
    )
    result.is_complete = result.is_complete and exports_succeeded
    return result
