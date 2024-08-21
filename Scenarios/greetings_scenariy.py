import requests
import telebot
from telebot import types
from telebot.types import Message
import utils
from DB import db_user, db_places
from OSM import osm_manager
from Keyboards import send_menu


class main_greetings_scenariy:

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot

    def start(self, message: Message):
        self.bot.clear_step_handler_by_chat_id(message.from_user.id)
        self.bot.send_message(message.from_user.id, '👋 Привет! Я - твой помощник по путешествиям. Давай знакомиться')
        age_message = self.bot.send_message(message.from_user.id,
                                            'Для начала, напиши свой возраст. Давай только честно ;)👇')
        self.bot.register_next_step_handler(age_message, self.select_age)

    def select_age(self, message: Message):
        age_text = message.text
        if not utils.is_int(age_text):
            age_message = self.bot.send_message(message.from_user.id,
                                                '❌ Мне кажется, ты ошибся :(\nВведи, пожалуйста, свой возраст целым числом 👇')
            self.bot.register_next_step_handler(age_message, self.select_age)
            return
        age = int(message.text)
        message_dop = ''
        if age < 18:
            message_dop = 'Ого, не совсем подходящий возраст для путешествий('
        else:
            message_dop = 'Отлично, хороший возраст для путешествий!'

        db_user.update_param_from_userid('Users', 'age', message.text, message.from_user.id, False)
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Поделиться локацией", request_location=True)
        keyboard.add(button_geo)
        country_message = self.bot.send_message(message.from_user.id,
                                                f'✅ {message_dop}\n\nТеперь напиши страну, в которой ты живёшь',
                                                reply_markup=keyboard)
        self.bot.register_next_step_handler(country_message, self.select_country)

    def address_not_found(self, id):
        self.bot.send_message(id, '😕 Адрес не был найден, попробуй ввести его вручную')

    def select_country(self, message: Message):

        if message.location is None:
            country = osm_manager.get_country(message.text)
            if country is None:
                country_message = self.bot.send_message(message.from_user.id,
                                                        f'❌ Упс, я не нашёл такой страны на картах. Попробуй ещё раз')
                self.bot.register_next_step_handler(country_message, self.select_country)
                return

            select_city_msg = self.bot.send_message(message.from_user.id,
                                                    f'✅ {country[0]} - прекрасная страна! А сейчас расскажи в каком городе ты живёшь',
                                                    reply_markup=types.ReplyKeyboardRemove())
            self.bot.register_next_step_handler(select_city_msg, self.select_city)

            db_places.add_place(message.from_user.id, country[1])
            db_user.update_param_from_userid('Users', 'country', country[0], message.from_user.id, True)
        else:
            try:
                locate = str(message.location.longitude) + ',' + str(message.location.latitude)

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

                info = requests.get('https://geocode-maps.yandex.ru/1.x/?apikey=636227ad-a114-4068-a821-47bb4cdc2ff2&format=json&geocode=' + locate, headers=headers)

                if len(info.json()['response']['GeoObjectCollection']['featureMember']) > 0:

                    country_name = ''
                    city_name = ''
                    components = \
                        info.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject'][
                            'metaDataProperty'][
                            'GeocoderMetaData']['Address']['Components']
                    for adress in components:

                        if adress['kind'] == 'country':
                            country_name = adress['name']
                        elif adress['kind'] == 'locality':
                            city_name = adress['name']

                    country = osm_manager.get_country(country_name)

                    if country is None:
                        self.address_not_found(message.chat.id)
                        return
                    city = osm_manager.get_city(city_name, country[0])
                    if city is None:
                        self.address_not_found(message.chat.id)
                        return
                    db_places.add_place(message.chat.id, country[1])
                    db_user.update_param_from_userid('Users', 'country', country[0], message.chat.id, True)
                    db_user.update_param_from_userid('Users', 'city', city[0], message.chat.id, True)
                    db_user.update_param_from_userid('Places', 'city_id', city[1], message.chat.id, False)

                    msg = self.bot.send_message(message.from_user.id,
                                                f"✅ Локация успешно определена!\n<b>{country[0]}, {city[0]}</b>\n\n📝 Теперь давай познакомимся поближе: напиши пару слов о себе, это будет описанием твоего профиля",
                                                parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
                    self.bot.register_next_step_handler(msg, self.select_bio)
                else:
                    self.address_not_found(message.chat.id)
            except:
                self.address_not_found(message.chat.id)


    def select_city(self, message: Message):

        city = osm_manager.get_city(message.text,
                                    db_user.get_value_from_user_id('Users', message.from_user.id, 'country'))
        if city is None:
            select_city_msg = self.bot.send_message(message.from_user.id,
                                                    f'❌ Ого, я не нашёл такого города в твоей стране 😳. Попробуй ещё раз')
            self.bot.register_next_step_handler(select_city_msg, self.select_city)
            return
        bio_msg = self.bot.send_message(message.from_user.id,
                                        f'✅ Принято!\n📝 Теперь давай познакомимся поближе: напиши пару слов о себе, это будет описанием твоего профиля')
        self.bot.register_next_step_handler(bio_msg, self.select_bio)

        db_user.update_param_from_userid('Users', 'city', city[0], message.from_user.id, True)
        db_user.update_param_from_userid('Places', 'city_id', city[1], message.from_user.id, False)

    def select_bio(self, message: Message):
        if message.text is None:
            bio_msg = self.bot.send_message(message.from_user.id,
                                            '❌ Текст не может быть пустым :(\nПопробуй составить буквенное описание своего профиля, и прислать его мне ещё раз')
            self.bot.register_next_step_handler(bio_msg, self.select_bio)
            return
        if len(message.text) == 0:
            bio_msg = self.bot.send_message(message.from_user.id,
                                            '❌ Текст не может быть пустым :(\nПопробуй составить буквенное описание своего профиля, и прислать его мне ещё раз')
            self.bot.register_next_step_handler(bio_msg, self.select_bio)
            return
        if len(message.text) > 500:
            bio_msg = self.bot.send_message(message.from_user.id,
                                            '❌ Упс, описание слишком большое 😬. Попробуй уменьшить его до 500 символов и отправить мне ещё раз')
            self.bot.register_next_step_handler(bio_msg, self.select_bio)
            return
        db_user.update_param_from_userid('Users', 'bio', message.text, message.from_user.id, True)
        send_menu(self.bot, message.from_user.id,
                  '🔥 Ооооотлично! Рад нашему знакомству! Давай немного расскажу про себя\n\n📖 Я умею планировать твои путешествия. Как это? Всё просто - ты вносишь локации, даты посещения мест, а я делаю всю работу: составляю маршрут, нахожу кафе и рестораны, узнаю погоду, а ещё я могу приглашать в ваши путешествия других пользователь и многое другое! Я очень полезный и все мои преимущества в одном сообщении не перечислить. Буду надеяться, что не потеряешься :)')
