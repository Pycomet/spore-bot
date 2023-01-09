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

        # logging.info("Google Sheet Connected! Fetch Complete")
        data = spreadsheet["values"]
        return data
    except Exception as e:
        logging.error("You do not have permission to access this spreadsheet")
        return []

def update_stock_spreadsheet(item, count, sheet):
    "Update The Stock availability"
    stk_data = get_spreadsheet(f'STOCK SHEET {sheet}')[3::]

    stock = db_client.get_stock(item, sheet)

    row = None
    col = None
    for i, row in enumerate(stk_data):
        if item in row:
            col = row.index(item)
            break
    
    if row is not None and col is not None:
        print(f'Row: {i+1}, Column: {col+1}') 

        try:
            range_ = f'STOCK SHEET {sheet}!B{i+1}'
            value_input_option = 'RAW'
            values = [[int(stock.available) - int(count)]]
            service = build("sheets", "v4", credentials=creds)
            request = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID, range=range_,
                valueInputOption=value_input_option, body={'values': values})

            # Execute the update request
            response = request.execute()

            print(f"Stock Sheet {sheet} Updated!")

            return True

        except Exception as e:
            logging.error("Failed to update stock into spreadsheet")
            return []


def write_order_to_spreadsheet(order: Order):
    orders = get_spreadsheet(f"ORDER SHEET {order.sheet}")
    num_rows = len(orders)
    try:
        service = build("sheets", "v4", credentials=creds)
        range = f"ORDER SHEET {order.sheet}!A{num_rows + 1}:I{num_rows + 1}"
        spreadsheet = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=SPREADSHEET_ID,
                range=range,
                valueInputOption='RAW',
                body= {
                    'values': [
                        [order.buyer, order.item, order.note, order.total, order.payment, order.date, order.address, order.created_at]
                    ]
                }
            )
            .execute()
        )

        logging.info(f"Created {order.sheet} Order For {order.item} Update Complete")

        update_stock_spreadsheet(
            item= order.item,
            count= order.total,
            sheet= order.sheet
        )

        return True
    except Exception as e:
        logging.error("Failed to write order into spreadsheet")
        return []





class DbClient:
    "For Reading, Updating & Deleting Spreadsheet Content"


    def get_orders(self) -> list:
        data = []

        for sheet_id in SHEETS:
            stk_data = get_spreadsheet(f'ORDER SHEET {sheet_id}')[1::]
            
            for item in stk_data:
                order = Order(
                    buyer=item[0],
                    item=item[1],
                    note=item[2],
                    total=item[3],
                    payment=item[4],
                    date= item[5],
                    address= item[6],
                    created_at= item[7],
                    sheet=sheet_id
                )
                data.append(order)

        return data

    def get_stocks(self) -> list:
        "Fetch all stock from spreadsheet"

        data = []
        for sheet_id in SHEETS:
            stk_data = get_spreadsheet(f'STOCK SHEET {sheet_id}')[3::]

            for item in stk_data:
                stock = Stock(
                    item=item[0],
                    available=item[1],
                    sheet=sheet_id
                )
                data.append(stock)
        return data

    
    def get_qty_code(self, sheet: str):
        "Get Quantity Code From Sheet"
        stk_data = get_spreadsheet(f'STOCK SHEET {sheet}')[1::]
        data = dict(zip(stk_data[0][2::], stk_data[1][2::]))
        return data



    def get_stock(self, item: str, sheet: str) -> Stock | None:
        "Validate a stock"
        stocks = self.get_stocks()
        for each in stocks:
            if each.item == item and each.sheet == sheet:
                return each
        return None

db_client = DbClient()
