from typing import Literal
import arcticdb
import yfinance as yf
import pandas as pd
import pandera as pa

Interval = Literal["1D", "1m", "5m", "30m", "60m"]


class Store(arcticdb.Arctic):

    @property
    def equity_prices(self) -> arcticdb.library.Library:
        return self.get_library(
            "equity_prices",
            create_if_missing=True,
            library_options=arcticdb.LibraryOptions(dedup=True, dynamic_schema=False),
        )

    def yield_data(
        self,
        universe: list[str],
        start: str,
        end: str,
        interval: Interval = "1D",
        instruments: pd.DataFrame | None = None,
    ):
        for symbol in universe:
            data = yf.Ticker(symbol).history(start=start, end=end, interval=interval)
            if data.empty:
                continue
            if instruments is not None:
                metadata = instruments.loc[symbol].to_dict()
            else:
                metadata = {}

            metadata.update({"Symbol": symbol})
            if not data.index.tzinfo:
                metadata.update({"timezone": data.index.tzinfo.zone})
                data = data.tz_localize("utc")
            else:
                metadata.update({"timezone": None})
                data = data.tz_convert("utc")
            yield symbol, data, metadata

    def seed(self, *args, **kwargs):

        for symbol, data, metadata in self.yield_data(*args, **kwargs):
            self.equity_prices.write(
                symbol,
                data,
                metadata=metadata,
            )

    def update(self, *args, **kwargs):
        universe = self.equity_prices.list_symbols()

        for symbol, data, metadata in self.yield_data(
            *args, universe=universe, **kwargs
        ):
            self.equity_prices.update(
                symbol,
                data,
                metadata=metadata,
                date_range=(data.index.min(), data.index.max()),
            )


class Universe:

    index = pa.Index(pa.String, nullable=False)
    Symbol = pa.Column(pa.String, nullable=False)

    @classmethod
    def from_link(cls, url: str) -> pd.DataFrame:
        return pd.read_html(url, index_col=0)[0]


if __name__ == "__main__":

    SP500_UNIVERSE = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    store = Store("lmdb://./.bars.db")

    tickers = Universe.from_link(SP500_UNIVERSE)

    store.seed(
        universe=tickers.index.to_list(),
        start="2024-03-01",
        end="2024-03-26",
        instruments=tickers,
        interval="30m",
    )
