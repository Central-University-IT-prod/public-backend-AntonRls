from telebot import TeleBot, types
from DB import db_notes


def send_notes_list(bot: TeleBot, id, travel_id, offset=0, message_id=0):
    notes = db_notes.get_notes(travel_id, id)
    offset = int(offset)
    if len(notes) == 0:
        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                     callback_data=f'travel_show`{travel_id}`edit'))
        bot.send_message(id, "У этого путешествия пока нет заметок :(", reply_markup=markup_inline)
        return

    markup_inline = types.InlineKeyboardMarkup()

    count = 0
    for i in range(offset, len(notes)):

        markup_inline.add(
            types.InlineKeyboardButton(text=notes[i][1],
                                       callback_data=f'notes_open`{travel_id}`{notes[i][2]}'))

        count += 1
        if count == 10:
            break

    if offset == 0 and offset + 10 < len(notes):
        markup_inline.add(
            types.InlineKeyboardButton(text='➡️',
                                       callback_data=f'notes_shownotes`{travel_id}`{offset + 10}')
        )

    elif offset + 10 < len(notes) and offset > 0:
        markup_inline.add(
            types.InlineKeyboardButton(text='⬅️',
                                       callback_data=f'notes_shownotes`{travel_id}`{offset - 10}'),
            types.InlineKeyboardButton(text='➡️',
                                       callback_data=f'notes_shownotes`{travel_id}`{offset + 10}'))
    elif offset + 10 >= len(notes) != 1 and offset != 0:
        markup_inline.add(types.InlineKeyboardButton(text='⬅️',
                                                     callback_data=f'notes_shownotes`{travel_id}`{offset - 10}'))
    markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                 callback_data=f'travel_show`{travel_id}`edit'))
    if message_id == 0:
        bot.send_message(id, '📋 Заметки к путешествию', reply_markup=markup_inline)
    else:
        bot.edit_message_text('📋 Заметки к путешествию', id, message_id, reply_markup=markup_inline)


def show_note_info(bot: TeleBot, id, message_id, travel_id, note_id, new_message=True):
    note_info = db_notes.get_note_info(travel_id, note_id)
    if note_info is None:
        bot.send_message(id, "Такая заметка не найдена")
        return
    markup_inline = types.InlineKeyboardMarkup()
    if str(id).strip() == travel_id.split('_')[0]:
        if note_info[2] == 0:
            markup_inline.add(types.InlineKeyboardButton(text='🔓 Сделать публичной',
                                                     callback_data=f'notes_unclosenote`{travel_id}`{note_id}'))
        else:
            markup_inline.add(types.InlineKeyboardButton(text='🔒 Сделать приватной',
                                                     callback_data=f'notes_closenote`{travel_id}`{note_id}'))
        markup_inline.add(types.InlineKeyboardButton(text='🗑 Удалить',
                                                 callback_data=f'notes_removenote`{travel_id}`{note_id}'))
    markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                 callback_data=f"notes_shownotes`{travel_id}`0`notedit"))

    if new_message:
        if note_info[1] is not None:
            if note_info[1].split('_')[0] == 'photo':
                bot.send_photo(id, open(note_info[1], 'rb'), note_info[0], reply_markup=markup_inline)
            else:
                bot.send_document(id, open(note_info[1], 'rb'),caption=note_info[0], reply_markup=markup_inline)
        else:
            bot.edit_message_text(note_info[0], id, message_id, reply_markup=markup_inline)
    else:
        bot.edit_message_reply_markup(id, message_id, reply_markup=markup_inline)