from telebot.types import CallbackQuery, LabeledPrice
from data.loader import bot, manager
from keyboards.inline import to_cart_menu


@bot.callback_query_handler(func=lambda call: "prev" in call.data)
def prev_products(callback: CallbackQuery):
    chat_id = callback.message.chat.id

    _, product_id, quantity = callback.data.split("_")
    price = manager.product.get_product_price(int(product_id))

    if int(quantity) <= 0:
        return

    bot.edit_message_reply_markup(
        chat_id,
        message_id=callback.message.message_id,
        reply_markup=to_cart_menu(
            product_id=int(product_id),
            current_quantity=int(quantity),
            price=int(price) * int(quantity)
        )
    )


@bot.callback_query_handler(func=lambda call: "next" in call.data)
def next_products(callback: CallbackQuery):
    chat_id = callback.message.chat.id

    _, product_id, quantity = callback.data.split("_")
    price = manager.product.get_product_price(int(product_id))

    product_total_quantity = manager.product.get_product_quantity(int(product_id))
    if int(quantity) > product_total_quantity:
        return

    bot.edit_message_reply_markup(
        chat_id,
        message_id=callback.message.message_id,
        reply_markup=to_cart_menu(
            product_id=int(product_id),
            current_quantity=int(quantity),
            price=int(price) * int(quantity)
        )
    )


@bot.callback_query_handler(func=lambda call: "cart" in call.data)
def add_to_cart(callback: CallbackQuery):
    chat_id = callback.message.chat.id

    user_id = manager.user.get_user_id(chat_id)
    cart_id = manager.cart.get_cart_id(user_id)

    _, product_id, quantity, price = callback.data.split("_")

    manager.cart_product.update(cart_id, int(product_id), int(price), int(quantity))
    bot.answer_callback_query(callback.id, "Добавлено")


@bot.callback_query_handler(func=lambda call: "pay" in call.data)
def pay(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = manager.user.get_user_id(chat_id)

    _, cart_id = callback.data.split("_")
    cart_products = manager.cart_product.show_cart_items(int(cart_id))
    total_price, _ = manager.cart.get_cart_info(user_id)

    cart_text = "Ваша заказы \n\n"

    for title, qty, price in cart_products:
        cart_text += f"""
Название: <i>{title}</i>

Цена: {price}
Кол-во: {qty}
"""

    try:
        bot.send_invoice(
            chat_id,
            title="Для оплаты",
            description=cart_text,
            invoice_payload="bot-defined invoice payload",
            provider_token="371317599:TEST:1677511303252",
            currency="UZS",
            prices=[LabeledPrice(label="Заказы", amount=int(str(total_price)+ "00"))],
            start_parameter="pay",
            is_flexible=False
        )
    except Exception as e:
        print(e)
