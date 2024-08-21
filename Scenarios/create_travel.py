import telebot
from telebot import types
from telebot.types import Message

from DB import db_user, db_travel
from UserManager import user_manager
from Keyboards import create_cancel_keyboard


class main_create_travel:
    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot

    def start(self, id):
        msg = self.bot.send_message(id,
                                    '🚉 Собираешься в путешествие? Хорошая идея! Давай для начала придумаем ему название',
                                    reply_markup=create_cancel_keyboard('travel'))
        self.bot.register_next_step_handler(msg, self.select_name_travel)

    def select_name_travel(self, message: Message):
        if message.text is None:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Необходимо придумать название для путешествия. Попробуй ещё раз',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.select_name_travel)
            return
        if len(message.text) > 50:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Название путешествия слишком длинное:(\nПопробуй его уложить в 50 символов',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.select_name_travel)
            return

        travel_id = db_travel.create_travel(message.from_user.id, message.text)
        user_manager.set_payload(message.from_user.id, travel_id)
        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(
            types.InlineKeyboardButton(text='❌ Отменить создание', callback_data=f'travel_cancel'))
        markup_inline.add(
            types.InlineKeyboardButton(text='🔜 Пропустить', callback_data=f'travel_skipenterdisc`{travel_id}'))

        msg = self.bot.send_message(message.from_user.id,
                                    'Интересное название! Давай теперь подумаем над описанием для путешествия',
                                    reply_markup=markup_inline)

        self.bot.register_next_step_handler(msg, self.select_description_travel)

    def select_description_travel(self, message: Message):
        if message.text is None:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Описание не может быть пустым',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.select_description_travel)
            return
        if len(message.text) > 299:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Описание слииииишком длинное, оно должно быть меньше 300 символов',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.select_description_travel)
            return
        travel_id = user_manager.get_payload(message.from_user.id)
        db_travel.update_travel_parm(message.from_user.id, travel_id, 'description', message.text)

        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(
            types.InlineKeyboardButton(text='➕ Добавить локацию', callback_data='travel_addlocation`' + travel_id))
        self.bot.send_message(message.from_user.id, '❓ А сейчас главный вопрос - куда собираемся ехать?',
                              reply_markup=markup_inline)
