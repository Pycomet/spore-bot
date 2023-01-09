from dataclasses import dataclass
from datetime import date


@dataclass
class Stock:
    "Stock Model From Spreadsheet"
    item: str = ""
    available: str = ""
    sheet: str = "" # Sheet ID (e.g X, Z)


@dataclass
class Order:
    "Bot Data Sheet Model"
    buyer: str = ""
    item: str = ""
    note: str = ""
    total: str = ""
    payment: str = ""
    date: str = ""
    address: str = ""
    created_at: str = ""
    sheet: str = "" # Sheet ID (e.g X, Z)



