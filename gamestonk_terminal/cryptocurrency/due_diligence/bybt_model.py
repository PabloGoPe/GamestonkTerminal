import json
import datetime as dt
import pandas as pd
import requests
from gamestonk_terminal import config_terminal as cfg


def get_open_interest_per_exchange(symbol: str, interval: int) -> pd.DataFrame:
    """Returns open interest by exchange for a certain symbol
    [Source: https://bybt.gitbook.io]

    Parameters
    ----------
    symbol : str
        Crypto Symbol to search open interest futures (e.g., BTC)
    interval : int
        Interval frequency (e.g., 0)

    Returns
    -------
    pd.DataFrame
        open interest by exchange and price
    """

    url = f"http://open-api.bybt.com/api/pro/v1/futures/openInterest/chart?&symbol={symbol.upper()}&interval={interval}"

    headers = {"bybtSecret": cfg.API_BYBT_KEY}

    response = requests.request("GET", url, headers=headers)

    if response.status_code == 200:
        res_json = json.loads(response.text)
        if res_json["msg"] == "success":
            data = res_json["data"]
            time = data["dateList"]
            time_new = []
            for elem in time:
                time_actual = dt.datetime.utcfromtimestamp(elem / 1000)
                time_new.append(time_actual)
            df = pd.DataFrame(
                data={"date": time_new, "price": data["priceList"], **data["dataMap"]}
            )
            df = df.set_index("date")
            return df
    return pd.DataFrame()
