import telebot
from telebot.types import Message, CallbackQuery

from DB import db_manager, db_user, db_user_full_info,db_dict
from Scenarios import greetings_scenariy, create_travel
from Keyboards import send_menu
from Handlers import travel_handler, notes_handler, exchange_handler, profile_handler
from Controllers import travel_controller, exchange_controller, profile_controller
from Handlers import payments_handler

db_manager.create_database()

bot = telebot.TeleBot('6714245611:AAF_43YtBTTScwj1A8xf_IHdQMT5f-Q7WeA')


@bot.message_handler(commands=['start'])
def start(message: Message):
    if db_user.is_new_user(message.from_user.id):
        db_user.register_user(message.from_user.id, message.from_user.username)
        greet = greetings_scenariy.main_greetings_scenariy(bot)
        greet.start(message)
    else:
        send_menu(bot, message.from_user.id, 'Добрый день, давно не виделись!')

    if db_user_full_info.is_new_info(message.from_user.id):
        db_user_full_info.add_info(message.from_user.id)
    db_dict.update_username(message.from_user.id, message.from_user.username)


@bot.message_handler(content_types=['text', 'document', 'audio'])
def new_message(message: Message):
    if db_user.is_new_user(message.from_user.id):
        db_user.register_user(message.from_user.id, message.from_user.username)
        greet = greetings_scenariy.main_greetings_scenariy(bot)
        greet.start(message)
    elif message.text == '✏️ Добавить путешествие':
        travel = create_travel.main_create_travel(bot)
        travel.start(message.from_user.id)
    elif message.text == '🌃 Мои путешествия':
        travel_controller.send_travel_list(bot, message.from_user.id)
    elif message.text == '🗂 Биржа путешествий':
        exchange_controller.open_exchange(bot, message.from_user.id, 0)
    elif message.text == '📱 Мой профиль':
        profile_controller.send_profile_info(message.from_user.id, bot)
    else:
        send_menu(bot, message.from_user.id, 'Воспользуйся меню и посети незабываемое путешествие!')

    if db_user_full_info.is_new_info(message.from_user.id):
        db_user_full_info.add_info(message.from_user.id)

    db_dict.update_username(message.from_user.id, message.from_user.username)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: CallbackQuery):
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    name = call.data.split('_')[0]
    data = call.data.split('_')[1]
    if len(call.data.split('_')) > 2:
        data += "_" + call.data.split('_')[2]
    if name == 'travel':
        travel = travel_handler.travel_handle(bot)
        travel.handle(data, call.from_user.id, call)
    elif name == 'nexttravel':
        travel_controller.send_travel_list(bot, call.from_user.id, int(data), call.message.message_id)
    elif name == 'notes':
        notes = notes_handler.notes_handle(bot)
        notes.handle(data, call.from_user.id, call)
    elif name == 'exchange':
        exchange = exchange_handler.exchange_handle(bot)
        exchange.handle(data, call.from_user.id, call)
    elif name == 'profile':
        profile = profile_handler.  profile_handle(bot)
        profile.handle(data, call.from_user.id, call)
    elif name == 'payments':
        payments = payments_handler.payments_handle(bot)
        payments.handle(data, call.from_user.id, call)

    db_dict.update_username(call.from_user.id, call.from_user.username)


bot.polling(none_stop=True, interval=0)
