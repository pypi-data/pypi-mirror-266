"""Uma source que obtém preços de fundos de investimento da CVM.

O ticker é o CNPJ do fundo de investimento, sem pontos, barras ou hífens
e com 14 dígitos, acrescido de zeros à esquerda, se necessário.
"""

import csv
import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from io import BytesIO
from typing import Iterator, TextIO
from zipfile import ZipFile

import requests

from ._cache import CACHE_BASE_PATH
from ._source import SourcePrice

_BASE_URL = "https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS"

_CACHE_PATH = CACHE_BASE_PATH / "beanprice_br" / "fi"
_CACHE_PATH.mkdir(parents=True, exist_ok=True)


def _is_in_current_month(date: date) -> bool:
    """Check if a given date is in the current month."""
    return date.year == date.today().year and date.month == date.today().month


_NON_DIGITS_REGEX = re.compile(r"\D")


def _cnpj_to_ticker(cnpj: str) -> str:
    return _NON_DIGITS_REGEX.sub("", cnpj).rjust(14, "0")


def _get_csv_from_cache_or_fetch(date: date) -> TextIO | None:
    """Try to get the CSV content for a given date from the cache.
    If not found, fetch from the source and store in the cache."""

    csv_filename = f"inf_diario_fi_{date.year}{date.month:02}.csv"

    cached_csv_path = _CACHE_PATH / csv_filename
    # If the file is in the cache, return its content.
    # But bypass the cache if date is in the current month.
    if cached_csv_path.exists() and not _is_in_current_month(date):
        return cached_csv_path.open("rt")

    # Otherwise, try fetching it from monthly zipped files:
    zip_filename = f"inf_diario_fi_{date.year}{date.month:02}.zip"
    response = requests.get(f"{_BASE_URL}/{zip_filename}")
    if response.status_code == 200:
        with ZipFile(BytesIO(response.content)) as zip_file:
            with zip_file.open(csv_filename) as csv_file:
                with cached_csv_path.open("wb") as cached_csv_file:
                    while chunk := csv_file.read(4096 * 16):
                        cached_csv_file.write(chunk)
                return cached_csv_path.open("rt")

    # If the request failed, but not because the file was not found, throw.
    if response.status_code not in (403, 404):
        response.raise_for_status()
        return None

    # If the file was not found, try fetching it from the yearly zipped files:
    zip_filename = f"HIST/inf_diario_fi_{date.year}.zip"
    response = requests.get(f"{_BASE_URL}/{zip_filename}")
    if response.status_code == 200:
        with ZipFile(BytesIO(response.content)) as zip_file:
            for month in range(1, 13):
                csv_filename = f"inf_diario_fi_{date.year}{month:02}.csv"
                if csv_filename not in zip_file.namelist():
                    continue

                with zip_file.open(csv_filename) as csv_file:
                    month_cached_csv_path = _CACHE_PATH / csv_filename
                    with month_cached_csv_path.open("wb") as cached_csv_file:
                        while chunk := csv_file.read(4096 * 16):
                            cached_csv_file.write(chunk)

            return cached_csv_path.open("rt")

    response.raise_for_status()
    return None


def _get_prices_from_csv(
    csv_file: TextIO, ticker: str, start_date: date, end_date: date
) -> Iterator[SourcePrice]:
    reader = csv.DictReader(csv_file, delimiter=";")
    for row in reader:
        file_ticker = _cnpj_to_ticker(row["CNPJ_FUNDO"])
        if file_ticker != ticker:
            continue

        dt = datetime.strptime(row["DT_COMPTC"], "%Y-%m-%d")
        if dt.date() < start_date or dt.date() > end_date:
            continue

        price = Decimal(row["VL_QUOTA"])
        yield SourcePrice(
            price=price, time=dt.replace(tzinfo=timezone.utc), quote_currency="BRL"
        )


def get_latest_prices(
    ticker: str, start_date: date, end_date: date
) -> Iterator[SourcePrice]:
    """Get the latest prices for a given ticker within a date range,
    in reverse chronological order."""

    # Start from the start of the month of the end date.
    current_date = end_date.replace(day=1)

    # Iterate over the months in reverse chronological order.
    while current_date >= start_date.replace(day=1):
        # Fetch the CSV content for the current month.
        csv_file = _get_csv_from_cache_or_fetch(current_date)

        if csv_file is None:
            raise ValueError(f"Failed to fetch CSV for {current_date}")

        # Parse the prices from the CSV content.
        prices = _get_prices_from_csv(csv_file, ticker, start_date, end_date)

        # Yield in reverse chronological order.
        yield from sorted(prices, key=lambda p: p.time or datetime.min, reverse=True)

        # Move to the previous month.
        current_date = (current_date + timedelta(days=-32)).replace(day=1)


_first_day_with_prices = date(2000, 1, 1)


class Source:
    def get_latest_price(self, ticker: str) -> SourcePrice | None:
        """Get the latest price for a given ticker."""
        ticker = _cnpj_to_ticker(ticker)
        return next(
            get_latest_prices(
                ticker, start_date=_first_day_with_prices, end_date=date.today()
            ),
            None,
        )

    def get_historical_price(self, ticker: str, dt: date) -> SourcePrice | None:
        """Get the price for a given ticker on a given date."""
        ticker = _cnpj_to_ticker(ticker)
        return next(
            get_latest_prices(ticker, start_date=_first_day_with_prices, end_date=dt),
            None,
        )

    def get_prices_series(
        self, ticker: str, start_date: date, end_date: date
    ) -> list[SourcePrice]:
        """Get the prices for a given ticker within a date range."""
        ticker = _cnpj_to_ticker(ticker)
        return list(reversed(list(get_latest_prices(ticker, start_date, end_date))))
