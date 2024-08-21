from telebot import TeleBot, types
from telebot.types import CallbackQuery
from DB import db_travel, db_exchange, db_dict
from Controllers import exchange_controller
from Handlers import travel_handler
class exchange_handle:
    def __init__(self, bot: TeleBot):
        self.bot = bot

    def handle(self, data, id, call: CallbackQuery):
        name = data.split('`')[0]

        if name == 'open':
            travel_id = data.split('`')[1]
            offset = int(data.split('`')[2])
            info_travel = db_travel.get_information(travel_id)
            if info_travel is None:
                return

            username = db_dict.get_username_from_id(travel_id.split('_')[0])
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(
                types.InlineKeyboardButton(text='🗺 Просмотреть локации',
                                           callback_data='travel_showlocations`' + travel_id + f'`0`exchange`{offset}'))
            markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                         callback_data=f'exchange_show`{offset}'))
            self.bot.edit_message_text(f'<b>Описание:</b>\n{info_travel[2]}\n\n<a href="https://t.me/{username}">Связаться с создателем путешествия</a>', id, call.message.message_id, reply_markup=markup_inline, parse_mode='html')
        elif name == 'show':
            offset = int(data.split('`')[1])
            exchange_controller.open_exchange(self.bot, id, offset, call.message.message_id)
        elif name == 'createexchange':
            travel_id = data.split('`')[1]
            db_exchange.add_to_exchange(travel_id, call.message.from_user.username, id)
            travel_handler.travel_handle(self.bot).handle(f'control`{travel_id}`edit', id, call)
        elif name == 'removefromexchange':
            travel_id = data.split('`')[1]
            db_exchange.remove_travel_from_exchange(travel_id)
            travel_handler.travel_handle(self.bot).handle(f'control`{travel_id}`edit', id, call)