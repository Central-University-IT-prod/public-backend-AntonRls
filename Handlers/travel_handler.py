import math
import time
import utils

from telebot import TeleBot, types
from telebot.types import Message, CallbackQuery
from datetime import date

from UserManager import user_manager
from Keyboards import create_cancel_keyboard
from DB import db_locations, db_travel, db_dict, db_invite_friend, db_places, db_exchange, db_user
from OSM import osm_manager
from utils import is_int
from Controllers import travel_controller, places_controller
from Parsers import weather_controller
from utils import to_unix_time, is_owner_travel



class travel_handle:
    def __init__(self, bot: TeleBot):
        self.bot = bot

    def handle(self, data, id, call: CallbackQuery):

        name = data.split('`')[0]
        if name == 'addlocation':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            msg = self.bot.send_message(id,
                                        '🚄 Через запятую напиши название страны и город, в который ты хочешь поехать\n\nНапример: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.select_locate)
            user_manager.set_payload(id, travel_id)
        elif name == 'skipenterdisc':
            travel_id = data.split('`')[1]
            db_travel.update_travel_parm(call.from_user.id, travel_id, 'description', 'не указано')
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(
                types.InlineKeyboardButton(text='➕ Добавить локацию', callback_data='travel_addlocation`' + travel_id))
            self.bot.edit_message_text('❓ А сейчас главный вопрос - куда собираемся ехать?', call.from_user.id,
                                       call.message.message_id,
                                       reply_markup=markup_inline)
        elif name == 'cancel':
            payload_object = user_manager.get_payload(id)
            payload = []
            if payload_object != None:
                payload = user_manager.get_payload(id).split('`')
            if len(payload) != 0:
                if len(payload) == 1:
                    info_travel = db_travel.get_information(payload[0])
                    if info_travel is not None:
                        if info_travel[2] is None and info_travel[1] is not None:
                            db_travel.remove_travel(call.from_user.id, payload[0])
                if len(payload) == 1 or len(payload) == 3:
                    self.bot.clear_step_handler_by_chat_id(id)
                else:
                    db_locations.remove_location(payload[0], payload[1])
                    self.bot.clear_step_handler_by_chat_id(id)
            self.bot.delete_message(id, call.message.message_id)
            self.bot.send_message(id, "✅ Отменено")
        elif name == 'show':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            is_edit = 'edit' in data
            travel_info = db_travel.get_information(travel_id)
            if travel_info is None:
                self.bot.send_message(id, 'Путешествие не найдено')
                return

            locations = db_locations.get_information(travel_id)
            count_location = len(locations)

            markup_inline = types.InlineKeyboardMarkup()
            if is_owner_travel(travel_id, id):
                markup_inline.add(
                    types.InlineKeyboardButton(text='➕ Добавить локацию',
                                               callback_data='travel_addlocation`' + travel_id),
                    types.InlineKeyboardButton(text='➕ Добавить заметку', callback_data='notes_addnote`' + travel_id))
            else:
                markup_inline.add(
                    types.InlineKeyboardButton(text='➕ Добавить заметку', callback_data='notes_addnote`' + travel_id))
            markup_inline.add(
                types.InlineKeyboardButton(text='🗺 Просмотреть локации',
                                           callback_data='travel_showlocations`' + travel_id + '`0'),
                types.InlineKeyboardButton(text='📑 Просмотреть заметки',
                                           callback_data='notes_shownotes`' + travel_id + '`0')
            )

            markup_inline.add(
                types.InlineKeyboardButton(text='🗺 Проложить маршрут',
                                           callback_data='travel_createmap`' + travel_id))

            markup_inline.add(types.InlineKeyboardButton(text='💰 Общие траты',
                                                         callback_data=f'payments_manager`{travel_id}'))
            if is_owner_travel(travel_id, id):
                markup_inline.add(
                    types.InlineKeyboardButton(text='⚙️ Управление путешествием',
                                               callback_data='travel_control`' + travel_id))

            text_message = f"ID: <code>{travel_id}</code>\nНазвание: <b>{travel_info[1]}</b>\nОписание:\n<b>{travel_info[2]}</b>\n\nКоличество локаций: <b>{count_location}</b>\nВремя в путешествии: <b>{utils.decline_number(db_travel.get_count_day_in_travel(travel_id))}</b>"
            if not is_edit:
                self.bot.send_message(id, text_message,
                                      reply_markup=markup_inline, parse_mode='html')
            else:
                self.bot.edit_message_text(text_message, id,
                                           call.message.message_id,
                                           reply_markup=markup_inline, parse_mode='html')
        elif name == 'control':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]

            markup_inline = types.InlineKeyboardMarkup()
            if is_owner_travel(travel_id, id):
                markup_inline.add(types.InlineKeyboardButton(text='📝 Изменить название',
                                                             callback_data='travel_changetitle`' + travel_id),
                                  types.InlineKeyboardButton(text='📝 Изменить описание',
                                                             callback_data='travel_changedescription`' + travel_id))
                markup_inline.add(
                    types.InlineKeyboardButton(text='📧 Пригласить друга',
                                               callback_data='travel_invitefriend`' + travel_id))
                if db_exchange.travel_in_exchange(travel_id):
                    markup_inline.add(types.InlineKeyboardButton(text='🔘 Убрать с биржи',
                                                                 callback_data=f'exchange_removefromexchange`{travel_id}'))
                else:
                    markup_inline.add(types.InlineKeyboardButton(text='⚪️ Разместить на бирже',
                                                                 callback_data=f'exchange_createexchange`{travel_id}'))
                markup_inline.add(
                    types.InlineKeyboardButton(text='🔍 Подобрать пользователей',
                                               callback_data=f'profile_search`{travel_id}`0'))
                markup_inline.add(
                    types.InlineKeyboardButton(text='🗞 Управление участниками',
                                               callback_data=f'travel_userscontroll`{travel_id}'))
                markup_inline.add(
                    types.InlineKeyboardButton(text='🗑 Удалить путешествие',
                                               callback_data='travel_removetravel`' + travel_id))
                markup_inline.add(
                    types.InlineKeyboardButton(text='🔙 Назад',
                                               callback_data='travel_show`' + travel_id+'`edit'))
            self.bot.edit_message_text('⌨️ Панель управления путешествием', id, call.message.message_id, reply_markup=markup_inline)
        elif name == 'userscontroll':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            markup_inline = types.InlineKeyboardMarkup()


            users = db_invite_friend.get_all_ids(travel_id)
            if len(users) == 0:
                markup_inline.add(
                    types.InlineKeyboardButton(text=f'🔙 Назад',
                                               callback_data=f'travel_control`{travel_id}`edit'))
                self.bot.edit_message_text('🌌 Вы единственный участник путешествия', id, call.message.message_id,
                                           reply_markup=markup_inline)

                return

            for user in users:
                username = db_dict.get_username_from_id(user)
                markup_inline.add(
                    types.InlineKeyboardButton(text=f'{username}',
                                               callback_data=f'travel_remuser`{travel_id}`{username}`{user}'))
            markup_inline.add(
                types.InlineKeyboardButton(text=f'🔙 Назад',
                                           callback_data=f'travel_control`{travel_id}`edit'))
            self.bot.edit_message_text('🌌 Участники путешествия', id, call.message.message_id, reply_markup=markup_inline)
        elif name == 'remuser':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            username = data.split('`')[2]
            user_id = data.split('`')[3]

            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(
                types.InlineKeyboardButton(text=f'✅ Да, удалить',
                                           callback_data=f'travel_remuserconfirm`{travel_id}`{user_id}'))
            markup_inline.add(
                types.InlineKeyboardButton(text=f'🔙 Нет, оставить',
                                           callback_data=f'travel_userscontroll`{travel_id}'))

            self.bot.edit_message_text(f'Удалить пользователя @{username}?', id, call.message.message_id, reply_markup=markup_inline)
        elif name == 'remuserconfirm':
            travel_id = data.split('`')[1]
            user_id = data.split('`')[2]
            title = db_travel.get_information(travel_id)[1]
            db_invite_friend.remove_user(user_id, travel_id)
            self.bot.send_message(user_id, f'⛔️ Упс, тебя удалили из путешествия "<b>{title}</b>"', parse_mode='html')
            self.handle(f'userscontroll`{travel_id}', id, call)
        elif name == 'changetitle':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            user_manager.set_payload(id, travel_id)
            msg = self.bot.send_message(id, '✏️ Придумай новое название для путешествия',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.change_title)
        elif name == 'changedescription':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            user_manager.set_payload(id, travel_id)
            msg = self.bot.send_message(id, '✏️ Придумай новое описание для путешествия',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.change_description)
        elif name == 'invitefriend':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            user_manager.set_payload(id, travel_id)
            msg = self.bot.send_message(id,
                                        "❗️Ты можешь пригласить друга в своё путешествие. Ему будет видна вся информация о нём\n\nДля приглашения, напиши имя друга в формате @username (друг должен быть зарегистрирован в боте)",
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.invite_friend)
        elif name == 'removetravel':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]

            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(
                types.InlineKeyboardButton(text='🗑 Да, удалить', callback_data='travel_removeconfirm`' + travel_id))
            markup_inline.add(
                types.InlineKeyboardButton(text='❌ Нет, оставить',
                                           callback_data='travel_hideremovemessage`' + travel_id))
            self.bot.edit_message_text('Уверены, что хотите удалить путешествие?', id, call.message.message_id,
                                       reply_markup=markup_inline)
        elif name == 'showalltravels':
            travel_controller.send_travel_list(self.bot, id, 0)
        elif name == 'removeconfirm':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            db_travel.remove_travel(id, travel_id)
            self.bot.delete_message(id, call.message.message_id)
            travel_controller.send_travel_list(self.bot, id, 0)
        elif name == 'hideremovemessage':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            self.handle(f'show`{travel_id}`edit', id, call)
        elif name == 'showlocations':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            offset = int(data.split('`')[2])
            locations = db_locations.get_information(travel_id)

            if len(locations) == 0:
                markup_inline = types.InlineKeyboardMarkup()
                if 'exchange' in data:
                    markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                                 callback_data=f'exchange_open`{travel_id}`0'))
                else:
                    markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                             callback_data=f'travel_show`{travel_id}`edit'))
                self.bot.send_message(id, 'К данному путешествию не добавлено локаций', reply_markup=markup_inline)
                return
            date = f"{locations[offset][3]}"
            if locations[offset][4] is None:
                date += "\n(1 день)"
            else:
                if locations[offset][4].strip() == '':
                    date += " (один день)"
                else:

                    days_count = math.ceil(
                        (to_unix_time(locations[offset][4]) - to_unix_time(locations[offset][3])) / 86400)
                    date += f"-{locations[offset][4]}\n"
                    date += f"({utils.decline_number(days_count)})"

            message = f"Локация №{offset + 1}\n\nМесто:\n<b>{locations[offset][1]}</b>\n\nДата прибывания:\n<b>{date}</b>"

            cords = db_places.get_cord(locations[offset][2])

            web_info = types.WebAppInfo(f"https://yandex.ru/maps/?ll={cords[1]},{cords[0]}&z=16&text=кафе и рестораны")
            hostels_info = types.WebAppInfo(f"https://yandex.ru/maps/?ll={cords[1]},{cords[0]}&z=16&text=отели")
            attraction_info = types.WebAppInfo(f"https://yandex.ru/maps/?ll={cords[1]},{cords[0]}&z=16&text=достопримечательности")
            markup_inline = types.InlineKeyboardMarkup()
            if offset == 0 and offset + 1 < len(locations):
                markup_inline.add(
                    types.InlineKeyboardButton(text='➡️',
                                               callback_data=f'travel_showlocations`{travel_id}`1'),
                    types.InlineKeyboardButton(text='⏩',
                                               callback_data=f'travel_showlocations`{travel_id}`{len(locations) - 1}')
                )

            elif offset + 1 < len(locations) and offset > 0:
                markup_inline.add(
                    types.InlineKeyboardButton(text='⏪',
                                               callback_data=f'travel_showlocations`{travel_id}`0'),
                    types.InlineKeyboardButton(text='⬅️',
                                               callback_data=f'travel_showlocations`{travel_id}`{offset - 1}'),
                    types.InlineKeyboardButton(text='➡️',
                                               callback_data=f'travel_showlocations`{travel_id}`{offset + 1}'),
                    types.InlineKeyboardButton(text='⏩',
                                               callback_data=f'travel_showlocations`{travel_id}`{len(locations) - 1}'),
                    row_width=4)
            elif offset + 1 == len(locations) and len(locations) != 1:
                markup_inline.add(types.InlineKeyboardButton(text='⏪',
                                                             callback_data=f'travel_showlocations`{travel_id}`0'),
                                  types.InlineKeyboardButton(text='⬅️',
                                                             callback_data=f'travel_showlocations`{travel_id}`{offset - 1}'))
            if is_owner_travel(travel_id, id):
                markup_inline.add(types.InlineKeyboardButton(text='📝 Изменить место',
                                                             callback_data=f'travel_changeplace`{travel_id}`{locations[offset][5]}`{offset}'))
                if is_owner_travel(travel_id, id): markup_inline.add(
                    types.InlineKeyboardButton(text='📝 Изменить дату прибывания',
                                               callback_data=f'travel_changedate`{travel_id}`{locations[offset][5]}`{offset}'))
            markup_inline.add(types.InlineKeyboardButton("🍕 Кафе и рестораны", web_app=web_info),
                              types.InlineKeyboardButton("🚪 Отели", web_app=hostels_info))
            markup_inline.add(types.InlineKeyboardButton("🏟 Достопримечательности", web_app=attraction_info))
            exchange_add = ''
            if 'exchange' in data:
                exchange_add = "exchange"
            markup_inline.add(types.InlineKeyboardButton(text='🌅 Прогноз погоды',
                                                         callback_data=f'travel_weatherinfo`{travel_id}`{locations[offset][5]}`{offset}`{exchange_add}'))
            if is_owner_travel(travel_id, id):
                markup_inline.add(types.InlineKeyboardButton(text='🗑 Удалить локацию',
                                                             callback_data=f'travel_removelocation`{travel_id}`{locations[offset][5]}`{offset}'))
            if 'exchange' in data:
                markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                             callback_data=f'exchange_open`{travel_id}`0'))
            else:
                markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                             callback_data=f'travel_show`{travel_id}`edit'))

            self.bot.edit_message_text(message, id, call.message.message_id, reply_markup=markup_inline,
                                       parse_mode='html')
        elif name == 'removelocation':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            location_id = data.split('`')[2]
            offset = int(data.split('`')[3])
            if offset - 1 >= 0:
                offset = offset - 1
            db_locations.remove_location(travel_id, location_id)
            if len(db_locations.get_information(travel_id)) == 0:
                self.bot.delete_message(id, call.message.message_id)
            self.handle(f"showlocations`{travel_id}`{offset}", id, call)
        elif name == 'weatherinfo':
            self.bot.clear_step_handler_by_chat_id(id)

            travel_id = data.split('`')[1]
            location_id = data.split('`')[2]
            offset = data.split('`')[3]

            location = db_locations.get_location_information(travel_id, location_id)
            if location is None:
                return
            try:
                start_data = location[3].split('.')

                if location[4] is not None:
                    end_data = location[4].split('.')
                else:
                    end_data = start_data
                place_id = location[2]
                cords = db_places.get_cord(place_id)
                exchange_add = ''
                if 'exchange' in data:
                    exchange_add = "exchange"
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(
                    types.InlineKeyboardButton(text='🔙 Назад',
                                               callback_data=f'travel_showlocations`{travel_id}`{offset}`edit`{exchange_add}'))
                msg = self.bot.edit_message_text("🔍 Поиск прогноза погоды", id, call.message.message_id)

                weathers_info = weather_controller.get_weather_interval(start_data[0], start_data[1], end_data[0],
                                                                        end_data[1], cords[0], cords[1])
                if len(weathers_info) < 30:
                    self.bot.edit_message_text("☀️ Прогноз погоды\n\n" + '\n\n'.join(weathers_info), id, msg.message_id,
                                           reply_markup=markup_inline, parse_mode='html')
                else:
                    is_first = True
                    while len(weathers_info) != 0:
                        message_add = ''
                        if is_first:
                            message_add = "☀️ Прогноз погоды\n\n"
                            is_first = False
                        temp_weather_info = []
                        count = 0
                        for i in range(0, len(weathers_info)):
                            temp_weather_info.append(weathers_info[i])
                            count += 1
                            if count >= 30:
                                break
                        for weather in temp_weather_info:
                            weathers_info.remove(weather)
                        if len(weathers_info) != 0:
                            self.bot.send_message(id, f"{message_add}"+'\n\n'.join(temp_weather_info), parse_mode='html')
                        else:
                            self.bot.send_message(id, f"{message_add}"+'\n\n'.join(temp_weather_info), reply_markup=markup_inline, parse_mode='html')

            except:
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(
                    types.InlineKeyboardButton(text='🔙 Путешествие',
                                               callback_data=f'travel_showlocations`{travel_id}`{offset}`edit'))
                self.bot.send_message(id, "Произошла ошибка при получении прогноза погоды",
                                      reply_markup=markup_inline, parse_mode='html')
        elif name == 'changeplace':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            location_id = data.split('`')[2]
            offset = 0
            msg = self.bot.send_message(id,
                                        '🚄 Через запятую напиши название страны и город, в который ты хочешь поехать\n\nНапример: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.update_locate)
            user_manager.set_payload(id, f"{travel_id}`{location_id}`{offset}")
        elif name == 'changedate':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            location_id = data.split('`')[2]
            offset = 0
            msg = self.bot.send_message(call.from_user.id,
                                        f"Напиши новые даты для этой локации\n\nДаты должны быть в формате: \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД-ДЕНЬ_ВЫЕЗДА.МЕСЯЦ.ГОД\"\nНапример\n\"16.06.2024-20.06.2024\"\nЕсли приезжаешь на один день, то напиши дату в формате\n\"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД\"",
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.update_data)
            user_manager.set_payload(id, f"{travel_id}`{location_id}`{offset}")
        elif name == 'allowinvite':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]

            self.bot.edit_message_text(
                f"🎉 Поздравляю! Ты успешно присоединился к путешествию. Его можно найти в разделе \"Мои путешествия\"",
                id, call.message.message_id)
            travel_name = db_travel.get_information(travel_id)[1]
            message_text = f"🔔 Пользователь @{call.from_user.username} присоединился к путешествию \"{travel_name}\""
            self.bot.send_message(travel_id.split('_')[0], message_text)
            temp_id = id
            ids = db_invite_friend.get_all_ids(travel_id)
            for id in ids:
                self.bot.send_message(id, message_text)
            db_invite_friend.insert_invite(travel_id, temp_id)
        elif name == 'deniedinvite':
            self.bot.clear_step_handler_by_chat_id(id)

            self.bot.delete_message(id, call.message.message_id)
        elif name == 'createmap':
            self.bot.clear_step_handler_by_chat_id(id)

            travel_id = data.split('`')[1]
            markup = types.InlineKeyboardMarkup()
            web_info = types.WebAppInfo(places_controller.create_link_from_home(travel_id, id))
            web_info_2 = types.WebAppInfo(places_controller.create_link_from_first(travel_id))
            markup.add(types.InlineKeyboardButton("✈️ Проложить маршрут от дома",
                                                  web_app=web_info))
            markup.add(types.InlineKeyboardButton("✈️ Проложить маршрут от первой точки",
                                                  web_app=web_info_2))
            self.bot.send_message(id, "❓ Откуда прокладываем маршрут?", reply_markup=markup)

    def invite_friend(self, message: Message):
        travel_id = user_manager.get_payload(message.from_user.id)
        username = message.text.replace('@', '')
        if username == message.from_user.username:
            msg = self.bot.send_message(message.from_user.id,
                                        "❌ Нельзя отправить приглашение самому себе :(",
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.invite_friend)
            return
        user_id = db_dict.get_user_from_username(username)
        if user_id is None:
            msg = self.bot.send_message(message.from_user.id,
                                        "❌ Пользователь не найден в боте! Попросите друга зарегистрироваться в боте",
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.invite_friend)
            return
        if not db_invite_friend.is_new_user(user_id, travel_id):
            msg = self.bot.send_message(message.from_user.id,
                                        "❌ Пользователь уже состоит в путешествии",
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.invite_friend)
            return
        travel_name = db_travel.get_information(travel_id)[1]
        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(
            types.InlineKeyboardButton(text='✅ Принять', callback_data=f'travel_allowinvite`' + travel_id))
        markup_inline.add(
            types.InlineKeyboardButton(text='❌ Отказаться', callback_data=f'travel_deniedinvite'))
        self.bot.send_message(user_id,
                              f"🔔 Пользователь @{message.from_user.username} приглашает тебя в путешествие \"{travel_name}\"",
                              reply_markup=markup_inline)
        self.bot.send_message(message.from_user.id, "✅ Приглашение успешно отправлено!")

    def update_data(self, message: Message):
        text = message.text.replace("\"", "").strip()
        payload = user_manager.get_payload(message.from_user.id).split('`')

        location_good = False
        if len(text.split('-')) == 1:
            if self._check_data(message.from_user.id, text, True):
                db_locations.update_param(payload[0], payload[1], 'start_date', f'{text}')
                db_locations.update_param(payload[0], payload[1], 'end_date', f'')
                location_good = True
        else:
            splited = text.split('-')
            if self._check_two_data(message.from_user.id, splited[0], splited[1], True):
                db_locations.update_param(payload[0], payload[1], 'start_date', f'{splited[0]}')
                db_locations.update_param(payload[0], payload[1], 'end_date', f'{splited[1]}')
                location_good = True
        if location_good:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(
                types.InlineKeyboardButton(text='➕ Добавить локацию', callback_data='travel_addlocation`' + payload[0]))
            markup_inline.add(
                types.InlineKeyboardButton(text='📜 Просмотреть путешествие', callback_data='travel_show`' + payload[0]))
            self.bot.send_message(message.from_user.id, "✏️ Дата успешно изменена! Что делаем дальше?",
                                  reply_markup=markup_inline)

    def update_locate(self, message: Message):
        splited = message.text.split(',')
        payload = user_manager.get_payload(message.from_user.id).split('`')
        if len(splited) < 2:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Через запятую напиши название страны и город, в который ты хочешь поехать\n\nНапример: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.update_locate)
            return
        country_name = osm_manager.get_country(splited[0].strip())
        if country_name is None:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ На своих картах я не нашёл такой страны\n\nНапоминаю, формат должен быть такой: Страна, город\nНапример: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.update_locate)
            return
        city_name = osm_manager.get_city(splited[1].strip(), country_name[0])
        if city_name is None:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ В указанной стране я не нашёл такого города\nНапоминаю, формат должен быть такой: Страна, город. Например: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.update_locate)
            return

        db_locations.update_param(payload[0], payload[1], "location_name", f"{country_name[0]}, {city_name[0]}")
        db_locations.update_param(payload[0], payload[1], "place_id", city_name[1], False)
        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(
            types.InlineKeyboardButton(text='➕ Добавить локацию', callback_data='travel_addlocation`' + payload[0]))
        markup_inline.add(
            types.InlineKeyboardButton(text='📜 Просмотреть путешествие', callback_data='travel_show`' + payload[0]))
        self.bot.send_message(message.from_user.id, "✏️ Место успешно изменено! Что делаем дальше?",
                              reply_markup=markup_inline)

    def change_description(self, message: Message):
        travel_id = user_manager.get_payload(message.from_user.id)
        if message.text is None:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Описание не может быть пустым',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.change_title)
        if len(message.text) > 300:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Ого! Описание путешествия слишком длинное, я такое не запомню :(\nПридумай покороче',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.change_title)
        db_travel.update_travel_parm(message.from_user.id, travel_id, "description", message.text)
        self.handle(f'show`{travel_id}', message.from_user.id, None)

    def change_title(self, message: Message):
        travel_id = user_manager.get_payload(message.from_user.id)
        if message.text is None:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Название не может быть пустым',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.change_title)
        if len(message.text) > 50:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Ого! Название путешествия слишком длинное, я такое не запомню :(\nПридумай покороче',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.change_title)
        db_travel.update_travel_parm(message.from_user.id, travel_id, "title", message.text)
        self.handle(f'show`{travel_id}', message.from_user.id, None)

    def select_locate(self, message: Message):
        splited = message.text.split(',')
        if len(splited) < 2:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Через запятую напиши название страны и город, в который ты хочешь поехать\n\nНапример: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.select_locate)
            return
        country_name = osm_manager.get_country(splited[0].strip())
        if country_name is None:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ На своих картах я не нашёл такой страны\n\nНапоминаю, формат должен быть такой: Страна, город\nНапример: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.select_locate)
            return
        city_name = osm_manager.get_city(splited[1].strip(), country_name[0])
        if city_name is None:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ В указанной стране я не нашёл такого города\nНапоминаю, формат должен быть такой: Страна, город. Например: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('travel'))
            self.bot.register_next_step_handler(msg, self.select_locate)
            return
        travel_id = user_manager.get_payload(message.from_user.id)
        location_id = db_locations.create_location(travel_id, f'{country_name[0]}, {city_name[0]}', city_name[1])
        is_first = ''
        if location_id == 1:
            is_first = ' первая'
        msg = self.bot.send_message(message.from_user.id,
                                    f"Супер,{is_first} точка в твоём путешествии поставлена. Теперь напиши даты, когда ты хочешь приехать сюда и уехать отсюда\n\nДаты должны быть в формате: \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД-ДЕНЬ_ВЫЕЗДА.МЕСЯЦ.ГОД\"\nНапример\n\"16.06.2024-20.06.2024\"\nЕсли приезжаешь на один день, то напиши дату в формате\n\"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД\"",
                                    reply_markup=create_cancel_keyboard('travel'))
        self.bot.register_next_step_handler(msg, self.select_data)
        user_manager.set_payload(message.from_user.id, f"{travel_id}`{location_id}")

    def _data_not_correct(self, id, is_update):
        msg = self.bot.send_message(id,
                                    f"❌ Формат даты не верный, пожалуйста, следуй шаблону\n\nДаты должны быть в формате: \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД-ДЕНЬ_ВЫЕЗДА.МЕСЯЦ.ГОД\", например \"16.06.2024-20.06.2024\". Если приезжаешь на один день, то напиши дату в формате \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД\"",
                                    reply_markup=create_cancel_keyboard('travel'))
        if not is_update:
            self.bot.register_next_step_handler(msg, self.select_data)
        else:
            self.bot.register_next_step_handler(msg, self.update_data)

    def _check_data(self, id, text, is_update=False):
        location_id = 0
        if is_update:
            location_id = int(user_manager.get_payload(id).split('`')[1])
        nodes = text.split('.')
        if len(nodes) != 3:
            self._data_not_correct(id, is_update)
            return False
        if not (is_int(nodes[0]) and is_int(nodes[1]) and is_int(nodes[2])):
            self._data_not_correct(id, is_update)
            return False
        day = int(nodes[0])
        month = int(nodes[1])
        year = int(nodes[2])

        if month > 12 or month < 1:
            self._data_not_correct(id, is_update)
            return False
        if day > 31 or day < 1:
            self._data_not_correct(id, is_update)
            return False
        if year < 2024:
            self._data_not_correct(id, is_update)
            return False
        try:
            d = date(year, month, day)
        except:
            self._data_not_correct(id, is_update)
            return False
        unixtime = time.mktime(d.timetuple())
        unix_time_now = time.mktime(d.today().timetuple())
        if unix_time_now > unixtime:
            msg = self.bot.send_message(id,
                                        f"❌ Дата не может быть в прошедшем времени\n\nДаты должны быть в формате: \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД-ДЕНЬ_ВЫЕЗДА.МЕСЯЦ.ГОД\", например \"16.06.2024-20.06.2024\". Если приезжаешь на один день, то напиши дату в формате \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД\"",
                                        reply_markup=create_cancel_keyboard('travel'))
            if not is_update:
                self.bot.register_next_step_handler(msg, self.select_data)
            else:
                self.bot.register_next_step_handler(msg, self.update_data)

            return False
        if not db_locations.data_is_empty(user_manager.get_payload(id).split('`')[0], unixtime, location_id):
            msg = self.bot.send_message(id,
                                        f"❌ Дата пересекается с другой датой путешествия\n\nДаты должны быть в формате: \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД-ДЕНЬ_ВЫЕЗДА.МЕСЯЦ.ГОД\", например \"16.06.2024-20.06.2024\". Если приезжаешь на один день, то напиши дату в формате \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД\"",
                                        reply_markup=create_cancel_keyboard('travel'))
            if not is_update:
                self.bot.register_next_step_handler(msg, self.select_data)
            else:
                self.bot.register_next_step_handler(msg, self.update_data)
            return False
        return True

    def _check_two_data(self, id, data1, data2, is_update=False):
        if not (self._check_data(id, data1, is_update) and self._check_data(id, data2, is_update)):
            return False
        location_id = 0
        if is_update:
            location_id = int(user_manager.get_payload(id).split('`')[1])
        data1 = date(int(data1.split('.')[2]), int(data1.split('.')[1]), int(data1.split('.')[0]))
        data2 = date(int(data2.split('.')[2]), int(data2.split('.')[1]), int(data2.split('.')[0]))
        if not db_locations.data_is_empty_interval(user_manager.get_payload(id).split('`')[0],
                                                   time.mktime(data1.timetuple()), time.mktime(data2.timetuple()),
                                                   location_id):
            msg = self.bot.send_message(id,
                                        f"❌ Дата пересекается с другой датой из путешествия\n\nДаты должны быть в формате: \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД-ДЕНЬ_ВЫЕЗДА.МЕСЯЦ.ГОД\", например \"16.06.2024-20.06.2024\". Если приезжаешь на один день, то напиши дату в формате \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД\"",
                                        reply_markup=create_cancel_keyboard('travel'))
            if not is_update:
                self.bot.register_next_step_handler(msg, self.select_data)
            else:
                self.bot.register_next_step_handler(msg, self.update_data)

            return False
        if time.mktime(data1.timetuple()) > time.mktime(data2.timetuple()):
            msg = self.bot.send_message(id,
                                        f"❌ Дата приезда не может быть позже даты выезда\n\nДаты должны быть в формате: \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД-ДЕНЬ_ВЫЕЗДА.МЕСЯЦ.ГОД\", например \"16.06.2024-20.06.2024\". Если приезжаешь на один день, то напиши дату в формате \"ДЕНЬ_ЗАЕЗДА.МЕСЯЦ.ГОД\"",
                                        reply_markup=create_cancel_keyboard('travel'))
            if not is_update:
                self.bot.register_next_step_handler(msg, self.select_data)
            else:
                self.bot.register_next_step_handler(msg, self.update_data)

            return False
        return True

    def select_data(self, message: Message):
        text = message.text.replace("\"", "").strip()
        payload = user_manager.get_payload(message.from_user.id).split('`')

        location_good = False
        if len(text.split('-')) == 1:
            if self._check_data(message.from_user.id, text):
                db_locations.update_param(payload[0], payload[1], 'start_date', f'{text}')
                location_good = True
        else:
            splited = text.split('-')
            if self._check_two_data(message.from_user.id, splited[0], splited[1]):
                db_locations.update_param(payload[0], payload[1], 'start_date', f'{splited[0]}')
                db_locations.update_param(payload[0], payload[1], 'end_date', f'{splited[1]}')
                location_good = True
        if location_good:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(
                types.InlineKeyboardButton(text='➕ Добавить локацию', callback_data='travel_addlocation`' + payload[0]))
            markup_inline.add(
                types.InlineKeyboardButton(text='📜 Просмотреть путешествие', callback_data='travel_show`' + payload[0]))
            self.bot.send_message(message.from_user.id, "✅ Локация успешно добавлена! Что делаем дальше?",
                                  reply_markup=markup_inline)
