"""
pip install --index-url=https://bcms.bloomberg.com/pip/simple blpapi
py -m pip install --upgrade --index-url=https://bcms.bloomberg.com/pip/simple blpapi
GFUT
"""

# packages
import re
import warnings
import pandas as pd
from enum import Enum
from typing import List, Optional, Tuple
from xbbg import blp

DEFAULT_START_DATE = pd.Timestamp('01Jan1959')


def fetch_fundamentals(tickers: List[str],
                       fields: List[str] = ('Security_Name', 'GICS_Sector_Name',)
                       ) -> pd.DataFrame:
    df = blp.bdp(tickers=tickers, flds=fields)
    df = df.loc[tickers, :]
    return df


def fetch_fields_timeseries_per_ticker(ticker: str,
                                       fields: List[str] = ('PX_OPEN', 'PX_HIGH', 'PX_LOW', 'PX_LAST',),
                                       CshAdjNormal: bool = True,
                                       CshAdjAbnormal: bool = True,
                                       CapChg: bool = True,
                                       start_date: pd.Timestamp = DEFAULT_START_DATE,
                                       end_date: pd.Timestamp = pd.Timestamp.now()
                                       ) -> Optional[pd.DataFrame]:

    try:
        # get bloomberg data adjusted for splits and divs
        field_data = blp.bdh(ticker, fields, start_date, end_date,
                             CshAdjNormal=CshAdjNormal, CshAdjAbnormal=CshAdjAbnormal, CapChg=CapChg)
    except:
        warnings.warn(f"could not get field_data for ticker={ticker}")
        return None

    try:
        field_data.columns = field_data.columns.droplevel(0)  # eliminate multiindex
    except:
        warnings.warn(f"something is wrong for ticker=r={ticker}")
        print(field_data)
        return None

    if len(fields) > 1:
        try:
            field_data = field_data[fields]  # rearrange columns
        except:
            # incomplete field data
            warnings.warn(f"could not get field_data for ticker={ticker}")
            return None
    else:
        pass

    field_data.index = pd.to_datetime(field_data.index)
    field_data.sort_index()
    return field_data


def fetch_field_timeseries_per_tickers(tickers: List[str],
                                       field: str = 'PX_LAST',
                                       CshAdjNormal: bool = True,
                                       CshAdjAbnormal: bool = True,
                                       CapChg: bool = True,
                                       start_date: pd.Timestamp = DEFAULT_START_DATE,
                                       end_date: pd.Timestamp = pd.Timestamp.now()
                                       ) -> Optional[pd.DataFrame]:

    #try:
        # get bloomberg data adjusted for splits and divs
    field_data = blp.bdh(tickers, field, start_date, end_date, CshAdjNormal=CshAdjNormal, CshAdjAbnormal=CshAdjAbnormal, CapChg=CapChg)
    #field_data = blp.bdh(tickers, field, start_date, end_date)
    # field_data = blp.bdp(tickers, field)
    #except:
    #   warnings.warn(f"could not get field_data for field={field}")
    #    return None

    try:
        field_data.columns = field_data.columns.droplevel(1)  # eliminate multiindex
    except:
        warnings.warn(f"something is wrong for field={field}")
        print(field_data)
        return None

    # make sure all columns are returns
    field_data = field_data.reindex(columns=tickers)
    field_data.index = pd.to_datetime(field_data.index)
    field_data = field_data.sort_index()
    return field_data


def fetch_active_futures(generic_ticker: str = 'ES1 Index',
                         first_gen: int = 1
                         ) -> Tuple[pd.Series, pd.Series]:
    """
    need to run with GFUT settings: roll = None
    bloomberg often fails to get joint data for two adjacent futures
    we need to split the index
    """
    atickers = [instrument_to_active_ticker(generic_ticker, num=first_gen),
                instrument_to_active_ticker(generic_ticker, num=first_gen + 1)]

    start_date = DEFAULT_START_DATE
    end_date = pd.Timestamp.now()
    price_datas = {}
    for aticker in atickers:
        price_data = fetch_fields_timeseries_per_ticker(ticker=aticker, fields=['PX_LAST'],
                                                        CshAdjNormal=False, CshAdjAbnormal=False, CapChg=False,
                                                        start_date=start_date, end_date=end_date)
        price_datas[aticker] = price_data.iloc[:, 0]
        start_date = price_data.index[0]
        end_date = price_data.index[-1]
    price_data = pd.DataFrame.from_dict(price_datas, orient='columns')

    return price_data.iloc[:, 0], price_data.iloc[:, 1]


def instrument_to_active_ticker(instrument: str = 'ES1 Index', num: int = 1) -> str:
    """
    ES1 Index to ES{num} Index
    Z1 Index to Z 1 Index
    """
    head = contract_to_instrument(instrument)
    ticker_split = instrument.split(' ')
    mid = "" if len(ticker_split[0]) > 1 else " "
    active_ticker = f"{head}{mid}{num} {ticker_split[-1]}"
    return active_ticker


def contract_to_instrument(future: str) -> str:
    """
    ES1 Index to ES Index
    """
    ticker_split_wo_num = re.sub('\d+', '', future).split()
    return ticker_split_wo_num[0]


class UnitTests(Enum):
    FUNDAMENTALS = 1
    FIELDS_PER_TICKER = 2
    FIELD_PER_TICKERS = 3
    ACTIVE_FUTURES = 4


def run_unit_test(unit_test: UnitTests):

    if unit_test == UnitTests.FUNDAMENTALS:
        df = fetch_fundamentals(tickers=['AAPL US Equity', 'BAC US Equity'],
                                fields=['Security_Name', 'GICS_Sector_Name', 'CRNCY'])
        print(df)

    elif unit_test == UnitTests.FIELDS_PER_TICKER:
        # df = fetch_fields_timeseries_per_ticker(ticker='USDJPYV1M BGN Curncy', fields=['PX_LAST'])
        # df = fetch_fields_timeseries_per_ticker(ticker='SPY US Equity', fields=['30DAY_IMPVOL_100.0%MNY_DF', 'PX_LAST'])
        # df = fetch_fields_timeseries_per_ticker(ticker='USDJPY Curncy', fields=['30DAY_IMPVOL_100.0%MNY_DF', 'PX_LAST'])
        df = fetch_fields_timeseries_per_ticker(ticker='ES1 Index', fields=['PX_LAST', 'FUT_DAYS_EXP'])
        print(df)

    elif unit_test == UnitTests.FIELD_PER_TICKERS:
        # df = fetch_field_timeseries_per_tickers(tickers=['AAPL US Equity', 'OCBC SP Equity', '6920 JP Equity'], field='30DAY_IMPVOL_100.0%MNY_DF')
        df = fetch_field_timeseries_per_tickers(tickers=['ES1 Index', 'ES2 Index', 'ES3 Index'], field='PX_LAST',
                                                CshAdjNormal=False, CshAdjAbnormal=False, CapChg=False)
        print(df)

        # this = blp.bds("ESA Index", "FUT_CHAIN")
        # this = blp.bds("SPY US Equity", "opt_chain", single_date_override="20191010")
        # print(this)

    elif unit_test == UnitTests.ACTIVE_FUTURES:
        # field_data = blp.active_futures('ESA Index', dt='1997-09-10')
        # print(field_data)

        field_data = fetch_active_futures(generic_ticker='S 1 Comdty')
        print(field_data)


if __name__ == '__main__':

    unit_test = UnitTests.ACTIVE_FUTURES

    is_run_all_tests = False
    if is_run_all_tests:
        for unit_test in UnitTests:
            run_unit_test(unit_test=unit_test)
    else:
        run_unit_test(unit_test=unit_test)
