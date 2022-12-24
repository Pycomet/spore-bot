import threading
from config import *
from utils import *

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
        f"Welcome back {msg.from_user.first_name}, \n\nWhat would like to order today? \nexample: B1",
        parse_mode="html"
    )   
    bot.register_next_step_handler(question, validateItem)


def validateItem(msg):
    "Check if the item exists"
    item = msg.text

    stock = db_client.get_stock(item)
    if stock == None:
        bot.send_message(
            msg.from_user.id,
            f"Invalid Stock Item. \n Click /order to try again.",
            parse_mode="html"
        )
    
    else:
        global order
        order.buyer = msg.from_user.username
        order.item = msg.text
        bot.send_message(
            msg.from_user.id,
            f"ITEM: {stock.item} \nPRICE: {stock.price} \nIN STOCK: {stock.available}",
            parse_mode="html"
        )

        question = bot.send_message(
            msg.chat.id,
            f"How many of this items do you wish to purchase ? \nexample: 2",
            parse_mode="html"
        )
        bot.register_next_step_handler(question, getItemCount)



def getItemCount(msg):
    "Get count"
    global order
    order.count = int(msg.text) or 1

    # Check availability
    stock = db_client.get_stock(order.item)
    
    amount_left = int(stock.available) - order.count

    if amount_left < 0:
        bot.send_message(
            msg.from_user.id,
            f"You are exceeding our inventory limit. The maximum available {stock.item} is {stock.available} \n Click /order to try again.",
            parse_mode="html"
        )

    else:
        # bot.reply_to(
        #     msg,
        #     f'{msg.text} by {order.buyer} for {order.count} {order.item}',
        # )

        question = bot.send_message(
            msg.from_user.id,
            "Provide your address? "
        )
        bot.register_next_step_handler(question, getAddress)


def getAddress(msg):
    "Get User Address"
    global order
    order.address = msg.text
    
    question = bot.send_message(
        msg.from_user.id,
        "Provide your preferred payment method ?"
    )
    bot.register_next_step_handler(question,  getPaymentMethod)

def getPaymentMethod(msg):
    "Get Payment Method"
    global order

    order.payment = msg.text
    order.date = str(datetime.now())

    stock = db_client.get_stock(order.item)

    bot.send_message(
        msg.from_user.id,
        f"ORDER: \n\nItem: {order.item} \nPrice: {stock.price} \nCount: {order.count} \nPayment Method: {order.payment} \nAddress: {order.address}\n\nProceed?",
        reply_markup=menu()
    )
    return order




@bot.callback_query_handler(func=lambda c: True)
def button_callback_answer(call):
    """
    Button Response
    """
    bot.send_chat_action(call.message.chat.id, "typing")

    global order

    if call.data == "yes":
        write_order_to_spreadsheet(order)
        bot.delete_message(call.from_user.id, call.message.message_id)

        bot.send_message(
            call.from_user.id,
            f"<b>Order Created!!</b>",
            parse_mode="html"
        )

        bot.send_message(
            int(ADMIN),
            f"<b>New Order Created For @{order.buyer}!!</b>",
            parse_mode="html"
        )
        order = Order()

    elif call.data == "no":
        order = Order()
        bot.delete_message(call.from_user.id, call.message.message_id)

        bot.send_message(
            call.from_user.id,
            f"<b>Order Cancelled!!</b>",
            parse_mode="html"
        )
    else:
        pass
