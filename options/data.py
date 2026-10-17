import logging
from enum import Enum
from typing import Optional, Tuple

import numpy as np
import pandas as pd

from options.common import export_df
from options.common import get_file_name
from options.download import get_ticker
from options.headers import __straddle_headers, final_headers
from options.result import Result, __get_result_of_output_files

log = logging.getLogger("options - data")
logging.basicConfig(level=logging.INFO)


class View(Enum):
    """Select which options views to export to CSV."""

    STRADDLE = 1
    STACKED = 2
    ALL = 3


stacked_name = 'options_chain'
straddle_name = 'straddle'


def __reformat(
        df: pd.DataFrame, option_type: str, date: str, symbol: str
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
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Fetch options chains and build straddle and stacked DataFrames.

    Match calls and puts by expiry date and strike for the straddle view.
    Stack call and put rows separately for the tabular view. This function
    prepares data in memory; it does not export files.

    Return two None values for a non-string symbol or a missing ticker.
    Chain-download errors are logged and processing continues with the
    next expiry. Subsequent transformation errors propagate to the caller.
    """
    if not isinstance(symbol, str):
        log.error("Please enter a symbol for the instrument")
        return None, None

    # Create the ticker used to retrieve expiry dates and options chains.
    yticker = get_ticker(symbol)
    if yticker is None:
        log.error(f"No data for {symbol} returned from the api")
        return None, None

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
                "Error getting options chain data for %s on %s: %s",
                symbol,
                date,
                exc,
            )

        if options_chain is not None:
            calls_df = __reformat(options_chain.calls, 'CALLS', date, symbol)
            calls_df_list.append(calls_df)

            puts_df = __reformat(options_chain.puts, 'PUTS', date, symbol)
            puts_df_list.append(puts_df)

            # Retain only strikes present in both calls and puts for this expiry.
            straddle_df = pd.DataFrame.merge(
                calls_df, puts_df, on=['expire_date', 'strike'], how='inner',
                suffixes=('_call', '_put'), sort=False
            )

            straddle_df_list.append(straddle_df)

    stacked_all_df = pd.DataFrame()
    straddle_all_df, calls_all_df, puts_all_df = None, None, None

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
        if df is not None:
            df.rename(columns=final_headers, inplace=True)

    return straddle_all_df, stacked_all_df


def get_options_view_df(
    symbol: str,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Download and return straddle and stacked DataFrames, in that order."""
    return __get_options_view_data(symbol)

def download_options_view(
        symbol: str,
        view_type: View = View.STRADDLE,
        folder: Optional[str] = None,
) -> Result:
    """Download both views and export the selected view or views to CSV.

    Use date-stamped filenames and omit DataFrame indices. The optional
    output folder must already exist. Return metadata based on output-file
    existence, using the existing result helper's completion rules.
    """
    straddle_view_df, all_df = get_options_view_df(symbol)

    file_name_straddle, file_name_stacked = None, None

    if view_type in (View.STRADDLE, View.ALL):
        file_name_straddle = get_file_name("{}_{}".format(straddle_name, symbol), True, folder)
        export_df(straddle_view_df, file_name_straddle, False)

    if view_type in (View.STACKED, View.ALL):
        file_name_stacked = get_file_name("{}_{}".format(stacked_name, symbol), True, folder)
        export_df(all_df, file_name_stacked, False)

    result = __get_result_of_output_files(file_name_straddle, file_name_stacked)
    return result
