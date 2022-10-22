import logging
from enum import Enum

import numpy as np
import pandas as pd

from options.common import export_df
from options.common import get_file_name
from options.download import get_ticker
from options.result import __get_result_of_output_files
from options.headers import __straddle_headers, final_headers


log = logging.getLogger("options - data")
logging.basicConfig(level=logging.INFO)


class View(Enum):
    STRADDLE = 1
    TABULAR = 2
    ALL = 3


def __reformat(df, option_type, date, symbol):
    df.insert(loc=0, column='option_type', value=option_type)
    df.insert(loc=1, column='expire_date', value=date)
    df.insert(loc=2, column='symbol', value=symbol)
    return df


def __get_options_view_data(symbol):
    """
        exports the options chain from yfinance api in the straddle view
    """
    if not isinstance(symbol, str):
        ValueError("Please enter a symbol for the instrument")
        return

    all_df = pd.DataFrame()

    yticker = get_ticker(symbol)

    if yticker is None:
        return False

    calls_df_list = []
    puts_df_list = []
    straddle_df_list = []

    expire_dates = yticker.options
    for date in expire_dates:
        log.info("{} downloading exercise date {}".format(symbol, date))
        options_chain = yticker.option_chain(date)

        calls_df = __reformat(options_chain.calls, 'CALLS', date, symbol)
        calls_df_list.append(calls_df)

        puts_df = __reformat(options_chain.puts, 'PUTS', date, symbol)
        puts_df_list.append(puts_df)

        straddle_df = pd.DataFrame.merge(calls_df, puts_df, on=['expire_date', 'strike'], how='inner',
                                         suffixes=('_call', '_put'), sort=False)

        straddle_df_list.append(straddle_df)
        del calls_df
        del puts_df

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
        all_df = pd.concat([all_df, calls_all_df])

    if puts_df_list:
        puts_all_df = pd.concat(puts_df_list, axis=0, ignore_index=True)
        all_df = pd.concat([all_df, puts_all_df])

    for df in [straddle_all_df, all_df]:
        df.rename(columns=final_headers, inplace=True)

    return straddle_all_df, all_df


def get_options_view_df(symbol):
    straddle_view_df, all_df = __get_options_view_data(symbol)
    return straddle_view_df, all_df


def download_options_view(symbol, viewtype=View.STRADDLE, folder=None):
    straddle_view_df, all_df = get_options_view_df(symbol)

    file_name_straddle, file_name_tabular = None, None

    if viewtype == View.STRADDLE or viewtype == View.ALL:
        file_name_straddle = get_file_name("straddle_{}".format(symbol), True, folder)
        export_df(straddle_view_df, file_name_straddle, False)

    if viewtype == View.TABULAR or viewtype == View.ALL:
        file_name_tabular = get_file_name("options_chain_{}".format(symbol), True, folder)
        export_df(all_df, file_name_tabular, False)

    result = __get_result_of_output_files(file_name_straddle, file_name_tabular)
    return result
