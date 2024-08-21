from telebot import TeleBot, types
from telebot.types import CallbackQuery, Message

from Handlers import travel_handler
from Keyboards import create_cancel_keyboard
from DB import db_notes
from UserManager import user_manager
from Controllers import note_controller


class notes_handle:
    def __init__(self, bot: TeleBot):
        self.bot = bot

    def handle(self, data, id, call: CallbackQuery):
        name = data.split('`')[0]
        if name == 'addnote':
            self.bot.clear_step_handler_by_chat_id(call.from_user.id)
            msg = self.bot.send_message(id, "✏️ Давай придумаем название для этой заметки",
                                        reply_markup=create_cancel_keyboard('notes'))
            self.bot.register_next_step_handler(msg, self.get_name_note)
            user_manager.set_payload(id, data.split('`')[1])
        elif name == 'shownotes':
            travel_id = data.split('`')[1]
            offset = data.split('`')[2]
            if 'notedit' in data:
                note_controller.send_notes_list(self.bot, id, travel_id, offset)
            else:
                note_controller.send_notes_list(self.bot, id, travel_id, offset, call.message.message_id)
        elif name == 'open':
            travel_id = data.split('`')[1]
            note_id = data.split('`')[2]
            is_new = True
            if 'edit' in data:
                is_new = False
            note_controller.show_note_info(self.bot, id, call.message.message_id, travel_id, note_id, is_new)
        elif name == 'unclosenote':
            travel_id = data.split('`')[1]
            note_id = data.split('`')[2]

            db_notes.update_param_note(travel_id, note_id, "is_public", "1")
            self.handle(f'open`{travel_id}`{note_id}`edit', id, call)
        elif name == 'closenote':
            travel_id = data.split('`')[1]
            note_id = data.split('`')[2]

            db_notes.update_param_note(travel_id, note_id, "is_public", "0")
            self.handle(f'open`{travel_id}`{note_id}`edit', id, call)
        elif name == 'removenote':
            travel_id = data.split('`')[1]
            note_id = data.split('`')[2]

            db_notes.remove_note(travel_id, note_id)

            self.handle(f'shownotes`{travel_id}`0`notedit', id, call)
        elif name == 'cancel':
            payload_object = user_manager.get_payload(id)
            payload = []
            if payload_object is not None:
                payload = user_manager.get_payload(id).split('`')
            if len(payload) == 2:
                db_notes.remove_note(payload[0], payload[1])
            self.bot.clear_step_handler_by_chat_id(id)
            self.bot.delete_message(id, call.message.message_id)

    def get_name_note(self, message: Message):
        if message.text is None:
            msg = self.bot.send_message(message.from_user.id, "❌ Название заметки не может быть пустым")
            self.bot.register_next_step_handler(msg, self.get_name_note)
            return
        if len(message.text) > 50:
            msg = self.bot.send_message(message.from_user.id,
                                        "❌ Название заметки слишком длинное, давай придумаем короче 50 символов?")
            self.bot.register_next_step_handler(msg, self.get_name_note)
            return
        travel_id = user_manager.get_payload(message.from_user.id)
        note_id = db_notes.create_note(travel_id, message.text)

        msg = self.bot.send_message(message.from_user.id,
                                    "📲 Отличное название! Теперь пришли фотографию/файл/текст, который будет содержать заметка",
                                    reply_markup=create_cancel_keyboard('notes'))
        self.bot.register_next_step_handler(msg, self.set_note_data)

        user_manager.set_payload(message.from_user.id, f"{travel_id}`{note_id}")

    def set_note_data(self, message: Message):
        payload = user_manager.get_payload(message.from_user.id).split('`')

        travel_id = payload[0]
        note_id = payload[1]
        if not (message.text is None):
            db_notes.update_param_note(travel_id, note_id, "description", message.text)
        if not (message.caption is None):
            db_notes.update_param_note(travel_id, note_id, "description", message.caption)
        if not (message.photo is None):
            file_info = self.bot.get_file(message.photo[-1].file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            src = f'photo_{travel_id}_{note_id}.{file_info.file_path.split(".")[-1]}'
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            db_notes.create_url_note(src, travel_id, note_id)
        if not (message.document is None):
            file_info = self.bot.get_file(message.document.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)

            src = f'file_{travel_id}_{note_id}.{message.document.file_name.split(".")[-1]}'
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            db_notes.create_url_note(src, travel_id, note_id)
        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(types.InlineKeyboardButton(text='🌃 Просмотреть путешествие',
                                                     callback_data='travel_show`' + travel_id + '`edit'))
        markup_inline.add(
            types.InlineKeyboardButton(text='➕ Добавить заметку', callback_data='notes_addnote`' + travel_id))
        self.bot.send_message(message.from_user.id, "Заметка успешно сохранена", reply_markup=markup_inline)
