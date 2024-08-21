from telebot import TeleBot, types
from Controllers import guide_controller
from DB import db_exchange, db_guide


def open_exchange(bot: TeleBot, id, offset, message_id=0):

    if db_guide.user_not_have_guide(id, 'exchange'):
        guide_controller.show_guide(bot, id,
                                    'exchange',
                                    'ℹ️ Биржа путешествий - это отличное место, чтобы найти себе путешествие. Здесь находятся путешествия, размещённые пользователями со всего мира',
                                    'exchange_show`0')
        return

    exchange_list = db_exchange.get_list_exchange()
    if len(exchange_list) == 0:
        bot.send_message(id, "Увы, сейчас биржа путешествий пуста :(")
        return
    markup_inline = types.InlineKeyboardMarkup()
    count = 0
    for i in range(offset, len(exchange_list)):
        markup_inline.add(
            types.InlineKeyboardButton(text=exchange_list[i][0], callback_data=f'exchange_open`{exchange_list[i][1]}`{offset}'))
        count += 1
        if count == 10:
            break

    if offset == 0 and offset + 10 < len(exchange_list):
        markup_inline.add(
            types.InlineKeyboardButton(text='➡️',
                                       callback_data=f'exchange_show`{offset + 10}')
        )

    elif offset + 10 < len(exchange_list) and offset > 0:
        markup_inline.add(
            types.InlineKeyboardButton(text='⬅️',
                                       callback_data=f'exchange_show`{offset - 10}'),
            types.InlineKeyboardButton(text='➡️',
                                       callback_data=f'exchange_show`{offset + 10}'))
    elif offset + 10 >= len(exchange_list) != 1 and offset != 0:
        markup_inline.add(types.InlineKeyboardButton(text='⬅️',
                                                     callback_data=f'exchange_show`{offset - 10}'))
    if message_id == 0:
        bot.send_message(id, "📖 Биржа путешествий", reply_markup=markup_inline)
    else:
        bot.edit_message_text("📖 Биржа путешествий", id, message_id, reply_markup=markup_inline)
