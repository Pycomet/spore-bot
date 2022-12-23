from dataclasses import dataclass
from datetime import date


@dataclass
class Stock:
    "Stock Model From Spreadsheet"
    item: str = ""
    price: str = ""
    available: str = ""
    qty_code: str = ""


@dataclass
class Order:
    "Bot Data Sheet Model"
    buyer: str = ""
    item: str = ""
    count: int = 1
    qty_code: str = ""
    total: str = ""
    payment: str = ""
    date: str = ""
    address: str = ""



