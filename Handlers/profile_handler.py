from telebot import TeleBot, types
from telebot.types import CallbackQuery, Message

import utils
from DB import db_user, db_user_full_info, db_places
from Keyboards import create_cancel_keyboard
from Controllers import profile_controller
from OSM import osm_manager


class profile_handle:
    def __init__(self, bot: TeleBot):
        self.bot = bot

    def handle(self, data, id, call: CallbackQuery):
        name = data.split('`')[0]

        if name == 'editage':
            self.bot.clear_step_handler_by_chat_id(id)
            msg = self.bot.send_message(id, "✏️ Напиши новый возраст", reply_markup=create_cancel_keyboard("profile"))
            self.bot.register_next_step_handler(msg, self.update_age)
        elif name == 'editplace':
            self.bot.clear_step_handler_by_chat_id(id)
            msg = self.bot.send_message(id, "✏️ Напиши новый адрес в формате Страна, Город\n\nНапример: Россия, Москва",
                                        reply_markup=create_cancel_keyboard("profile"))
            self.bot.register_next_step_handler(msg, self.update_place)
        elif name == 'editgender':
            self.bot.clear_step_handler_by_chat_id(id)

            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(text='🚹 Мужской', callback_data=f'profile_updategender`1'),
                              types.InlineKeyboardButton(text='🚺 Женский', callback_data=f'profile_updategender`2'))
            markup_inline.add(types.InlineKeyboardButton(text='🔶 Не указан', callback_data=f'profile_updategender`3'))
            markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data=f'profile_showprofile'))

            self.bot.edit_message_text("✏️ Выбрать пол", id, call.message.message_id,
                                       reply_markup=markup_inline)
        elif name == 'updategender':
            number_gender = int(data.split('`')[1])
            db_user_full_info.update_param(call.from_user.id, 'gender', number_gender, False)
            self.handle('showprofile', id, call)
        elif name == 'showprofile':
            profile_controller.send_profile_info(id, self.bot, call.message.message_id)
        elif name == 'editinterests':
            interests = ['рыбалка', 'охота', 'туризм', 'IT', 'наука', 'фильмы', 'чтение', 'транспорт', 'спорт',
                         'фотографии']
            interests_user_text = db_user_full_info.get_param(id, 'interests')
            interests_user = []
            if interests_user_text is not None:
                interests_user = interests_user_text.split(',')
            for i in range(len(interests_user)):
                interests_user[i] = interests_user[i].strip()
            markup_inline = types.InlineKeyboardMarkup()

            for item in interests:
                if item in interests_user:
                    markup_inline.add(
                        types.InlineKeyboardButton(text=f'🔘 {item}', callback_data=f'profile_removeinteres`{item}'))
                else:
                    markup_inline.add(
                        types.InlineKeyboardButton(text=f'⚪️ {item}', callback_data=f'profile_addinteres`{item}'))
            markup_inline.add(types.InlineKeyboardButton(text='✅ Сохранить', callback_data=f'profile_showprofile'))
            self.bot.edit_message_text("✏️ Интересы", id, call.message.message_id, reply_markup=markup_inline)
        elif name == 'addinteres':
            interes = data.split('`')[1]
            interests_user_text = db_user_full_info.get_param(id, 'interests')
            interests_user = []
            interests_user_temp = []
            if interests_user_text is not None:
                interests_user_temp = interests_user_text.split(',')
            for i in range(len(interests_user_temp)):
                if interests_user_temp[i].strip() != "" and interests_user_temp[i].strip() != "None":
                    interests_user.append(interests_user_temp[i])
            interests_user.append(interes)
            db_user_full_info.update_param(id, 'interests', utils.list_to_str(interests_user), True)
            self.handle('editinterests', id, call)
        elif name == 'removeinteres':
            interes = data.split('`')[1]
            interests_user_text = db_user_full_info.get_param(id, 'interests')
            interests_user = []
            interests_user_temp = []
            if interests_user_text is not None:
                interests_user_temp = interests_user_text.split(',')
            for i in range(len(interests_user_temp)):
                if interests_user_temp[i].strip() != "" and interests_user_temp[i].strip() != "None":
                    interests_user.append(interests_user_temp[i].strip())
            try:
                interests_user.remove(interes.strip())
            except:
                pass
            db_user_full_info.update_param(id, 'interests', utils.list_to_str(interests_user), True)
            self.handle('editinterests', id, call)
        elif name == 'editbio':
            self.bot.clear_step_handler_by_chat_id(id)
            msg = self.bot.send_message(id, "✏️ Напиши новое описание", reply_markup=create_cancel_keyboard("profile"))
            self.bot.register_next_step_handler(msg, self.update_bio)
        elif name == 'cancel':
            self.bot.clear_step_handler_by_chat_id(id)
            profile_controller.send_profile_info(call.from_user.id, self.bot, call.message.message_id)
        elif name == 'search':
            travel_id = data.split('`')[1]
            offset = int(data.split('`')[2])
            profile_controller.search_users(id, self.bot, offset, travel_id, call.message.message_id)

    def update_bio(self, message: Message):
        if message.text is None:
            bio_msg = self.bot.send_message(message.from_user.id,
                                            '❌ Текст не может быть пустым :(\nПопробуй составить буквенное описание своего профиля, и прислать его мне ещё раз',
                                            reply_markup=create_cancel_keyboard("profile"))
            self.bot.register_next_step_handler(bio_msg, self.update_bio)
            return
        if len(message.text) == 0:
            bio_msg = self.bot.send_message(message.from_user.id,
                                            '❌ Текст не может быть пустым :(\nПопробуй составить буквенное описание своего профиля, и прислать его мне ещё раз',
                                            reply_markup=create_cancel_keyboard("profile"))
            self.bot.register_next_step_handler(bio_msg, self.update_bio)
            return
        if len(message.text) > 500:
            bio_msg = self.bot.send_message(message.from_user.id,
                                            '❌ Упс, описание слишком большое 😬. Попробуй уменьшить его до 500 символов и отправить мне ещё раз',
                                            reply_markup=create_cancel_keyboard("profile"))
            self.bot.register_next_step_handler(bio_msg, self.update_bio)
            return
        db_user.update_param_from_userid('Users', 'bio', message.text, message.from_user.id, True)
        profile_controller.send_profile_info(message.from_user.id, self.bot)

    def update_age(self, message: Message):
        age_text = message.text
        if not utils.is_int(age_text):
            age_message = self.bot.send_message(message.from_user.id,
                                                '❌ Мне кажется, ты ошибся :(\nВведи, пожалуйста, свой возраст целым числом 👇',
                                                reply_markup=create_cancel_keyboard('profile'))
            self.bot.register_next_step_handler(age_message, self.update_age)
            return
        age = int(message.text)
        if age < 1:
            age_message = self.bot.send_message(message.from_user.id,
                                                '❌ Возраст не может быть отрицательным или равным нулю :(\nВведи, пожалуйста, свой возраст целым числом 👇',
                                                reply_markup=create_cancel_keyboard('profile'))
            self.bot.register_next_step_handler(age_message, self.update_age)
            return
        db_user.update_param_from_userid('Users', 'age', age, message.from_user.id, False)
        profile_controller.send_profile_info(message.from_user.id, self.bot)

    def update_place(self, message: Message):
        splited = message.text.split(',')
        if len(splited) < 2:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Через запятую напиши название страны и город, в который ты хочешь поехать\n\nНапример: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('profile'))
            self.bot.register_next_step_handler(msg, self.update_place)
            return
        country_name = osm_manager.get_country(splited[0].strip())
        if country_name is None:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ На своих картах я не нашёл такой страны\n\nНапоминаю, формат должен быть такой: Страна, город\nНапример: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('profile'))
            self.bot.register_next_step_handler(msg, self.update_place)
            return
        city_name = osm_manager.get_city(splited[1].strip(), country_name[0])
        if city_name is None:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ В указанной стране я не нашёл такого города\nНапоминаю, формат должен быть такой: Страна, город. Например: Россия, Москва',
                                        reply_markup=create_cancel_keyboard('profile'))
            self.bot.register_next_step_handler(msg, self.update_place)
            return
        db_places.update_place_info(message.from_user.id, 'country_id', country_name[1])
        db_places.update_place_info(message.from_user.id, 'city_id', city_name[1])
        db_user.update_param_from_userid('Users', 'country', country_name[0], message.from_user.id, True)
        db_user.update_param_from_userid('Users', 'city', city_name[0], message.from_user.id, True)

        profile_controller.send_profile_info(message.from_user.id, self.bot)
