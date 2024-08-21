from telebot import TeleBot, types
from DB import db_payments


def send_list_payments(travel_id, bot: TeleBot, id, message_id, offset):
    payments = db_payments.get_list_payments(travel_id)
    markup_inline = types.InlineKeyboardMarkup()
    if len(payments) == 0:
        markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                     callback_data=f'payments_manager`{travel_id}`edit'))
        bot.edit_message_text('⛔️В текущем путешествии пока не добавлены траты', id, message_id, reply_markup=markup_inline)
        return

    if offset >= len(payments):
        markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                     callback_data=f'payments_manager`{travel_id}`edit'))
        bot.edit_message_text('⛔️ Траты не найдены', id, message_id, reply_markup=markup_inline)
        return

    count = 0
    for i in range(offset, len(payments)):
        markup_inline.add(types.InlineKeyboardButton(text=f'{payments[i][1]} ({payments[i][2]})',
                                                     callback_data=f'payments_open`{travel_id}`{payments[i][0]}'))
        count += 1
        if count == 10:
            break

    if offset == 0 and offset + 10 < len(payments):
        markup_inline.add(
            types.InlineKeyboardButton(text='➡️',
                                       callback_data=f'payments_listpayments`{travel_id}`{offset+10}')
        )

    elif offset + 10 < len(payments) and offset > 0:
        markup_inline.add(
            types.InlineKeyboardButton(text='⬅️',
                                       callback_data=f'payments_listpayments`{travel_id}`{offset-10}'),
            types.InlineKeyboardButton(text='➡️',
                                       callback_data=f'payments_listpayments`{travel_id}`{offset+10}'))
    elif offset + 10 >= len(payments) != 1 and offset != 0:
        markup_inline.add(types.InlineKeyboardButton(text='⬅️',
                                                     callback_data=f'payments_listpayments`{travel_id}`{offset-10}'))
    markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                 callback_data=f'payments_manager`{travel_id}`edit'))
    bot.edit_message_text("💸 Траты в путешествии", id, message_id, reply_markup=markup_inline)