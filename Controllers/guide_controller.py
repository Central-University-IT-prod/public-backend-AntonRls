from telebot import TeleBot, types
from DB import db_guide


def show_guide(bot: TeleBot, user_id, guide_name, guide_text, data_continue):
    db_guide.add_guide(user_id, guide_name)

    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.add(
        types.InlineKeyboardButton(text='✅ Продолжить', callback_data=data_continue))
    bot.send_message(user_id, guide_text, reply_markup=markup_inline)