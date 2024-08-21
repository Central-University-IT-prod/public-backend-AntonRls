from telebot import TeleBot, types
from telebot.types import Message
from DB import db_travel, db_guide
from Controllers import guide_controller


def send_travel_list(bot: TeleBot, id, offset=0, message_id=0):
    if db_guide.user_not_have_guide(id, 'travel'):
        guide_controller.show_guide(bot, id,
                                    'travel',
                                    'ℹ️ В данном разделе ты можешь посмотреть список своих путешествий и отредактировать их',
                                    'travel_showalltravels')
        return

    travelles = db_travel.get_travel_list(id)
    if len(travelles) == 0:
        bot.send_message(id, "У тебя пока нет путешествий :(")
        return

    markup_inline = types.InlineKeyboardMarkup()

    count = 0
    for i in range(offset, len(travelles)):

        markup_inline.add(
            types.InlineKeyboardButton(text=travelles[i][1],
                                       callback_data=f'travel_show`{travelles[i][0]}'))
        count += 1
        if count == 10:
            break

    if offset == 0 and offset + 10 < len(travelles):
        markup_inline.add(
            types.InlineKeyboardButton(text='➡️',
                                       callback_data=f'nexttravel_{offset + 10}')
        )

    elif offset + 10 < len(travelles) and offset > 0:
        markup_inline.add(
            types.InlineKeyboardButton(text='⬅️',
                                       callback_data=f'nexttravel_{offset - 10}'),
            types.InlineKeyboardButton(text='➡️',
                                       callback_data=f'nexttravel_{offset + 10}'))
    elif offset + 10 >= len(travelles) != 1 and offset != 0:
        markup_inline.add(types.InlineKeyboardButton(text='⬅️',
                                                     callback_data=f'nexttravel_{offset - 10}'))
    if message_id == 0:
        bot.send_message(id, '📋 Список ваших путешествий', reply_markup=markup_inline)
    else:
        bot.edit_message_text('📋 Список ваших путешествий', id, message_id, reply_markup=markup_inline)
