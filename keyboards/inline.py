from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from data.loader import manager


def to_cart_menu(product_id, price, current_quantity=0):
    markup = InlineKeyboardMarkup()

    product_quantity = manager.product.get_product_quantity(product_id)

    markup.add(
        InlineKeyboardButton(text="-", callback_data=f"prev_{product_id}_{current_quantity - 1}"),
        InlineKeyboardButton(text=f"{current_quantity}/{product_quantity}", callback_data=f"empty?"),
        InlineKeyboardButton(text="+", callback_data=f"next_{product_id}_{current_quantity + 1}"),
        InlineKeyboardButton(text="Заказать", callback_data=f"cart_{product_id}_{current_quantity}_{price}")
    )
    return markup


def pay_btn(cart_id):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="Оплатить", callback_data=f"pay_{cart_id}")
    markup.add(btn)
    return markup
