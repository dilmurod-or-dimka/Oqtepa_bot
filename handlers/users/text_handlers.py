from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from data.loader import bot, manager
from keyboards.default import start_menu, categories_menu, get_product_by_categories
from keyboards.inline import to_cart_menu


@bot.message_handler(func=lambda msg: msg.text == "Регистрация")
def get_reg(message: Message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Напиши ваше имя")
    bot.register_next_step_handler(message, get_name)


def get_name(message: Message):
    chat_id = message.chat.id

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton(text="Отправить контакт", request_contact=True))

    bot.send_message(chat_id, "Отправьте мне свой контакат", reply_markup=kb)
    bot.register_next_step_handler(message, register, message.text)


def register(message: Message, name):
    chat_id = message.chat.id
    phone_number = message.contact.phone_number

    manager.user.add_user(name, phone_number, chat_id)
    user_id = manager.user.get_user_id(chat_id)
    manager.cart.add_user_id(user_id)

    bot.send_message(chat_id, "Регестрация завершена", reply_markup=start_menu(chat_id))


@bot.message_handler(func=lambda msg: msg.text == "Сделать заказ")
def start_get_order(message: Message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Выберите категорию 👇👇👇", reply_markup=categories_menu())


@bot.message_handler(func=lambda msg: msg.text in manager.category.get_categories() or msg.text.lower() == "назад")
def select_category(message: Message):
    chat_id = message.chat.id
    if message.text.lower() == "назад":
        bot.send_message(chat_id, "Выберите действие", reply_markup=start_menu(chat_id))
        return

    category_id = manager.category.get_category_id(message.text)
    bot.send_message(chat_id, f"Товары категории: {message.text}", reply_markup=get_product_by_categories(category_id))
    bot.register_next_step_handler(message, get_product_info)


def get_product_info(message: Message):
    chat_id = message.chat.id
    if message.text.lower() == "назад":
        start_get_order(message)
        return

    product_info = manager.product.get_product_info(message.text)
    if not product_info:
        bot.send_message(chat_id, "Извинись")
        bot.register_next_step_handler(message, get_product_info)
        return

    product_id, img_url, price, quantity, description = product_info

    bot.send_message(chat_id, f"""
{img_url}
{message.text}

Цена: {price}
Кол-во: {quantity}

{description[:300]}
""", reply_markup=to_cart_menu(product_id, price=price))


@bot.message_handler(func=lambda msg: msg.text == "Заказы")
def show_cart(message: Message):
    chat_id = message.chat.id
    user_id = manager.user.get_user_id(chat_id)
    cart_id = manager.cart.get_cart_id(user_id)

    cart_products = manager.cart_product.show_cart_items(cart_id)

    if not cart_products:
        bot.send_message(chat_id, "Заказов нет")
        return

    bot.send_message(chat_id, "Ваши заказы")

    cart_text = "Ваши заказы \n\n"

    for title, qty, price in cart_products:
        cart_text += f"""
Название: <i>{title}</i>

Цена: {price}
Кол-во: {qty}
"""

    bot.send_message(chat_id, cart_text, parse_mode="HTML")
    bot.send_message(chat_id, "Чтобы оформить заказ, нажмите /make_order")
    bot.send_message(chat_id, "Чтобы очистить корзину, нажмите /clear_cart")
