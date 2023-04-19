from telebot.types import Message
from data.loader import bot, manager
from keyboards.default import start_menu
from keyboards.inline import pay_btn


@bot.message_handler(commands=['start'])
def start(message: Message):
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    bot.send_message(chat_id, f"Привет, {first_name}", reply_markup=start_menu(chat_id))


@bot.message_handler(commands=['make_order'], chat_types='private')
def make_order(message: Message):
    chat_id = message.chat.id
    user_id = manager.user.get_user_id(chat_id)
    cart_id = manager.cart.get_cart_id(user_id)

    cart_products = manager.cart_product.show_cart_items(cart_id)
    total_price, total_quantity = manager.cart.get_cart_info(user_id)

    if not cart_products:
        bot.send_message(chat_id, "Корзина пуста")
        return

    cart_text = "Ваша корзина \n\n"

    for title, qty, price in cart_products:
        cart_text += f"""
Название: <i>{title}</i>

Цена: {price}
Кол-во: {qty}
"""

    cart_text += f"""
Общее кол-во товаров: {total_quantity} шт
Обшая стоимость товаров: {total_price} сум
"""

    bot.send_message(chat_id, cart_text, parse_mode="HTML", reply_markup=pay_btn(cart_id))


@bot.message_handler(commands=['clear_cart'], chat_types='private')
def clear_cart(message: Message):
    chat_id = message.chat.id
    user_id = manager.user.get_user_id(chat_id)
    cart_id = manager.cart.get_cart_id(user_id)
    manager.cart.clear_cart(cart_id)
    bot.send_message(chat_id, "Корзина была очищена")

