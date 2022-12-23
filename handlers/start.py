import threading
from config import *
from utils import *

# def start_menu():
#     keyboard = types.InlineKeyboardMarkup(row_width=2)

#     a = types.InlineKeyboardButton("Club Request", callback_data="request")
#     b = types.InlineKeyboardButton("Chip Request", callback_data="chip")
#     c = types.InlineKeyboardButton("Rake Back", callback_data="rake_back")
#     d = types.InlineKeyboardButton("View All Clubs", callback_data="all_clubs")
#     e = types.InlineKeyboardButton("Transactions", callback_data="payment")
#     # e = types.InlineKeyboardButton("🔙 Go Back" callback_data="back")

#     keyboard.add(a, b, c, d, e)
#     return keyboard

order = Order()


@bot.message_handler(commands=["start", "order"])
def startbot(msg):
    "Entry point of the bot discussion -- https://ibb.co/1Mvm7GN"

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
        order.buyer = msg.from_user.username
        order.item = msg.text
        bot.send_message(
            msg.from_user.id,
            f"ITEM: {stock.item} \nPRICE: {stock.price} \nIN STOCK: {stock.available}",
            parse_mode="html"
        )

        question = bot.send_message(
            msg.chat.id,
            f"How many of this items do you wish to purchase ? \nexample: ",
            parse_mode="html"
        )
        bot.register_next_step_handler(question, getItemCount)



def getItemCount(msg):
    "Get count"
    order.count = int(msg.text)
    bot.reply_to(
        msg,
        f'{msg.text} by {order.buyer} for {order.count} {order.item}',
    )


# @bot.callback_query_handler(func=lambda c: True)
# def button_callback_answer(call):
#     """
#     Button Response
#     """
#     bot.send_chat_action(call.message.chat.id, "typing")

#     if call.data == "request":
#         pass
#     else:
#         pass
