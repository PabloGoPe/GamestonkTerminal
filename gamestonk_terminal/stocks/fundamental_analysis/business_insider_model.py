"""Business Insider Model"""
__docformat__ = "numpy"

import requests
from bs4 import BeautifulSoup
import pandas as pd
from rapidfuzz import fuzz
from gamestonk_terminal.helper_funcs import get_user_agent


def get_management(ticker: str) -> pd.DataFrame:
    """Get company managers from Business Insider

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    pd.DataFrame
        Dataframe of managers
    """
    url_market_business_insider = (
        f"https://markets.businessinsider.com/stocks/{ticker.lower()}-stock"
    )
    text_soup_market_business_insider = BeautifulSoup(
        requests.get(
            url_market_business_insider, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    found_h2s = {}

    for next_h2 in text_soup_market_business_insider.findAll(
        "h2", {"class": "header-underline"}
    ):
        next_table = next_h2.find_next_sibling("table", {"class": "table"})

        if next_table:
            found_h2s[next_h2.text] = next_table

    if found_h2s.get("Management") is None:
        print(f"No management information in Business Insider for {ticker}")
        print("")
        return pd.DataFrame()

    l_titles = []
    for s_title in found_h2s["Management"].findAll(
        "td", {"class": "table__td text-right"}
    ):
        if any(c.isalpha() for c in s_title.text.strip()) and (
            "USD" not in s_title.text.strip()
        ):
            l_titles.append(s_title.text.strip())

    l_names = []
    for s_name in found_h2s["Management"].findAll(
        "td", {"class": "table__td table--allow-wrap"}
    ):
        l_names.append(s_name.text.strip())

    df_management = pd.DataFrame(
        {"Name": l_names[-len(l_titles) :], "Title": l_titles},
        columns=["Name", "Title"],
    )

    df_management["Info"] = "-"
    df_management["Insider Activity"] = "-"
    df_management = df_management.set_index("Name")

    for s_name in df_management.index:
        df_management.loc[s_name][
            "Info"
        ] = f"http://www.google.com/search?q={s_name} {ticker.upper()}".replace(
            " ", "%20"
        )

    s_url_base = "https://markets.businessinsider.com"
    for insider in text_soup_market_business_insider.findAll(
        "a", {"onclick": "silentTrackPI()"}
    ):
        for s_name in df_management.index:
            if fuzz.token_set_ratio(s_name, insider.text.strip()) > 70:
                df_management.loc[s_name]["Insider Activity"] = (
                    s_url_base + insider.attrs["href"]
                )
    return df_management
