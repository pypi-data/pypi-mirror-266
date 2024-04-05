from datetime import datetime
from decimal import Decimal
from typing import NamedTuple

SourcePrice = NamedTuple(
    "SourcePrice",
    [
        ("price", Decimal),
        ("time", datetime | None),
        ("quote_currency", str | None),
    ],
)
