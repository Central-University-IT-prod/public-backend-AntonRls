from telebot import TeleBot, types


def send_menu(bot: TeleBot, id, message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn1 = types.KeyboardButton('✏️ Добавить путешествие')
    btn2 = types.KeyboardButton('🌃 Мои путешествия')
    btn3 = types.KeyboardButton('🗂 Биржа путешествий')
    btn4 = types.KeyboardButton('📱 Мой профиль')
    markup.add(btn1, btn2, btn3, btn4)

    bot.send_message(id, message, reply_markup=markup, parse_mode='html')


def create_cancel_keyboard(sub_id):
    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.add(
        types.InlineKeyboardButton(text='❌ Отменить', callback_data=f'{sub_id}_cancel'))
    return markup_inline
