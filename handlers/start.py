import threading
from config import *
from utils import *
import time

def menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    a = types.InlineKeyboardButton("Confirm Order", callback_data="yes")
    b = types.InlineKeyboardButton("Cancel Order", callback_data="no")

    keyboard.add(a, b)
    return keyboard


order = Order()

@bot.message_handler(commands=["start", "order"])
def startbot(msg):
    "Entry point of the bot discussion -- https://ibb.co/1Mvm7GN"
    print(msg.chat.id)

    bot.send_chat_action(msg.from_user.id, "typing")

    if hasattr(msg, "message_id") and msg.chat.type != 'group':
        chat, m_id = get_received_msg(msg)
        bot.delete_message(chat.id, m_id)

    question = bot.send_message(
        msg.chat.id,
        f"Welcome back {msg.from_user.first_name}, \n\nWhat would like to order today? \nFormat: HUB, ITEM, QTY CODE, PAYMENT METHOD, ADDRESS, DATE TIME PICK UP, NOTES(Optional) \
            \n\nExample: <b>X, F203, D, CASH, ADDRESS, JAN 2 7PM, NOTES IF ANY</b> \n\n(For more than 1 order): <b>X, F203, D, CASH, ADDRESS, JAN 2 7PM, NOTES IF ANY | X, D22, E | X, B4, Q</b> ",
        parse_mode="html"
    )   
    bot.register_next_step_handler(question, validateItem)


def validateItem(msg):
    "Check if the item exists"
    orders_list = msg.text.split("|")

    bot.send_chat_action(msg.from_user.id, "typing")

    # Process first order
    first_order = orders_list[0]
    first_order_items = [i.strip() for i  in first_order.split(",")]

    if len(first_order_items) not in [6, 7]:
        bot.send_message(
            msg.from_user.id,
            f"Invalid Inputs On Order. \n Click /order to try again.",
            parse_mode="html"
        )
        return
          
    elif first_order_items[0] not in SHEETS:
        bot.send_message(
            msg.from_user.id,
            f"Invalid HUB. \n Click /order to try again.",
            parse_mode="html"
        )
        return

    stock = db_client.get_stock(first_order_items[1], first_order_items[0])
    if stock == None:
        bot.send_message(
            msg.from_user.id,
            f"Invalid Stock Item. \n Click /order to try again.",
            parse_mode="html"
        )
        
    else:

        first_order = Order()
        first_order.buyer = msg.from_user.username
        first_order.item = first_order_items[1]
        first_order.sheet = first_order_items[0]
        # calculate total from qty_code
        qty_codes = db_client.get_qty_code(first_order_items[0])
        first_order.total = qty_codes[first_order_items[2]]
        first_order.payment = first_order_items[3]
        first_order.address = first_order_items[4]
        first_order.date = first_order_items[5]
        first_order.created_at = str(datetime.now())
        if len(first_order_items) == 7:
            first_order.note = first_order_items[6]

        bot.send_message(
            msg.from_user.id,
            f"ORDER DETAILS: \n\nStock {stock.sheet} Item: {stock.item} \nQuantity: {first_order.total} \nPayment Method: {first_order.payment} \nDate Time Pick Up: {first_order.date} \nAddress: {first_order.address}",
            parse_mode="html"
        )
        bot.send_chat_action(msg.from_user.id, "typing")

        stock = db_client.get_stock(item=first_order.item, sheet=first_order.sheet)

        new_available = int(stock.available) - int(first_order.total)

        if new_available >= 0:

            # UPDATE STOCK SHEETS

            write_order_to_spreadsheet(first_order)

            bot.send_message(
                msg.from_user.id,
                f"<b>Order Created!!</b>",
                parse_mode="html"
            )

            bot.send_message(
                int(ADMIN),
                f"<b>New Order Created For @{first_order.buyer}!!</b>",
                parse_mode="html"
            )
        
        else:
            bot.send_message(
                msg.from_user.id,
                f"<b>Order Canceled! Only {stock.available} items available</b>",
                parse_mode="html"
            )

    

    for raw_order in orders_list[1:]:
        bot.send_chat_action(msg.from_user.id, "typing")

        r_items = raw_order.split(",")
        items = [i.strip() for i in r_items]

        if len(items) != 3:
            bot.send_message(
                msg.from_user.id,
                f"Invalid Inputs. \n Click /order to try again.",
                parse_mode="html"
            )
            continue  
        elif items[0] not in SHEETS:
            bot.send_message(
                msg.from_user.id,
                f"Invalid HUB. \n Click /order to try again.",
                parse_mode="html"
            )
            continue  

        stock = db_client.get_stock(items[1], items[0])
        if stock == None:
            bot.send_message(
                msg.from_user.id,
                f"Invalid Stock Item. \n Click /order to try again.",
                parse_mode="html"
            )
            continue
        
        else:
            order = Order()
            order.buyer = msg.from_user.username
            order.item = items[1]
            order.sheet = items[0]
            # calculate total from qty_code
            qty_codes = db_client.get_qty_code(items[0])
            order.total = qty_codes[items[2]]
            order.payment = first_order.payment
            order.address = first_order.address
            order.date = first_order.date
            order.created_at = str(datetime.now())

            bot.send_message(
                msg.from_user.id,
                f"ORDER DETAILS: \n\nStock {stock.sheet} Item: {stock.item} \nQuantity: {order.total} \nPayment Method: {order.payment} \nDate Time Pick Up: {order.date} \nAddress: {order.address}",
                parse_mode="html"
            )
            bot.send_chat_action(msg.from_user.id, "typing")

            stock = db_client.get_stock(item=order.item, sheet=order.sheet)

            new_available = int(stock.available) - int(order.total)

            if new_available >= 0:

                # UPDATE STOCK SHEETS

                write_order_to_spreadsheet(order)

                bot.send_message(
                    msg.from_user.id,
                    f"<b>Order Created!!</b>",
                    parse_mode="html"
                )

                bot.send_message(
                    int(ADMIN),
                    f"<b>New Order Created For @{order.buyer}!!</b>",
                    parse_mode="html"
                )
            
            else:
                bot.send_message(
                    msg.from_user.id,
                    f"<b>Order Canceled! Only {stock.available} items available</b>",
                    parse_mode="html"
                )
            continue


# @bot.callback_query_handler(func=lambda c: True)
# def button_callback_answer(call):
#     """
#     Button Response
#     """
#     bot.send_chat_action(call.message.chat.id, "typing")

#     global order

#     if call.data == "yes":





#     elif call.data == "no":
#         order = Order()
#         bot.delete_message(call.from_user.id, call.message.message_id)

#         bot.send_message(
#             call.from_user.id,
#             f"<b>Order Canceled!!</b>",
#             parse_mode="html"
#         )
#     else:
#         pass
