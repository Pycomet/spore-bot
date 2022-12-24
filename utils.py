from config import *
from models import *


def get_received_msg(msg):
    "Delete This Message"
    message_id = msg.message_id
    chat = msg.chat
    return chat, message_id


def get_spreadsheet(name: str):
    try:
        service = build("sheets", "v4", credentials=creds)
        spreadsheet = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=SPREADSHEET_ID, range=name
            )
            .execute()
        )

        logging.info("Google Sheet Connected! Fetch Complete")
        data = spreadsheet["values"]
        return data
    except Exception as e:
        logging.error("You do not have permission to access this spreadsheet")
        return []


def write_order_to_spreadsheet(order: Order):
    orders = get_spreadsheet("ORDER SHEET")
    num_rows = len(orders)
    try:
        service = build("sheets", "v4", credentials=creds)
        spreadsheet = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'ORDER SHEET!A{num_rows + 1}:G{num_rows + 1}',
                valueInputOption='RAW',
                body= {
                    'values': [
                        [order.buyer, order.item, order.qty_code, order.count, order.payment, order.date, order.address]
                    ]
                }
            )
            .execute()
        )

        logging.info(f"Created Order For {order.item} Update Complete")
        return True
    except Exception as e:
        logging.error("Failed to write order into spreadsheet")
        return []





class DbClient:
    "For Reading, Updating & Deleting Spreadsheet Content"


    def get_orders(self) -> list:
        stk_data = get_spreadsheet('ORDER SHEET')[1::]
        data = []

        for item in stk_data:
            order = Order(
                buyer=item[0],
                item=item[1],
                count=item[2],
                total=item[3],
                payment=item[4],
                date= item[5],
                address= item[6]
            )
            data.append(order)
        return data

    def get_stocks(self) -> list:
        "Fetch all stock from spreadsheet"
        stk_data = get_spreadsheet('STOCK SHEET')[1::]
        data = []

        for item in stk_data:
            stock = Stock(
                item=item[0],
                price=f'${item[1]}',
                available=item[2],
                qty_code=item[4]
            )
            data.append(stock)
        return data

    def create_order(self) -> Order:
        pass


    def get_stock(self, item: str) -> Stock | None:
        "Validate a stock"
        stocks = self.get_stocks()
        for each in stocks:
            if each.item == item:
                return each
        return None

db_client = DbClient()
