from datetime import date

from telebot import TeleBot, types
from telebot.types import CallbackQuery, Message

from Controllers import payments_controller, guide_controller
from UserManager import user_manager
from Keyboards import create_cancel_keyboard
from DB import db_payments, db_dict, db_invite_friend, db_travel, db_guide
from utils import is_int, is_float


class payments_handle:
    def __init__(self, bot: TeleBot):
        self.bot = bot

    def handle(self, data, id, call: CallbackQuery):
        name = data.split('`')[0]

        if name == 'manager':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            if db_guide.user_not_have_guide(id, 'payments'):
                guide_controller.show_guide(self.bot, id,
                                            'payments',
                                            'ℹ️ Траты - это неотъемлемая часть любого путешествия. В данном разделе ты можешь создавать траты, делить их между участниками путешествия и конечно же просматривать их ',
                                            f'payments_manager`{travel_id}')
                return



            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(
                types.InlineKeyboardButton(text='➕ Добавить трату',
                                           callback_data=f'payments_createpayment`{travel_id}'))
            markup_inline.add(
                types.InlineKeyboardButton(text='🗂 Список трат',
                                           callback_data=f'payments_listpayments`{travel_id}'))

            markup_inline.add(
                types.InlineKeyboardButton(text='📒 Список долгов',
                                           callback_data=f'payments_debtorme`{travel_id}'),

                types.InlineKeyboardButton(text='📒 Список должников',
                                           callback_data=f'payments_mydebtors`{travel_id}')
            )
            markup_inline.add(
                types.InlineKeyboardButton(text='🔙 Назад',
                                           callback_data=f'travel_show`{travel_id}`edit'))
            self.bot.edit_message_text("💵 Менеджер трат", id, call.message.message_id, reply_markup=markup_inline)
        elif name == 'debtorme':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            debtors = db_payments.i_debtors(travel_id, id)
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(
                types.InlineKeyboardButton(text='🔙 Назад',
                                           callback_data=f'payments_manager`{travel_id}`edit'))
            if len(debtors.keys()) == 0:
                self.bot.edit_message_text("Вы никому не должны 👌", id, call.message.message_id,
                                           reply_markup=markup_inline)
                return
            message = "<b>Вы должны</b>\n\n"
            for debtor in debtors.keys():
                message += f"@{debtor}: {debtors[debtor]}₽\n"
            self.bot.edit_message_text(message, id, call.message.message_id, reply_markup=markup_inline,
                                       parse_mode='html')
        elif name == 'mydebtors':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            debtors = db_payments.my_debtors(travel_id, id)
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(
                types.InlineKeyboardButton(text='🔙 Назад',
                                           callback_data=f'payments_manager`{travel_id}`edit'))
            if len(debtors.keys()) == 0:

                self.bot.edit_message_text("Список должников пуст 👌",id, call.message.message_id, reply_markup=markup_inline)
                return
            message = "<b>Ваши должники</b>\n\n"
            for debtor in debtors.keys():
                message += f"@{debtor}: {debtors[debtor]}₽\n"
            self.bot.edit_message_text(message, id, call.message.message_id, reply_markup=markup_inline, parse_mode='html')
        elif name == 'listpayments':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            offset = 0
            if len(data.split('`')) > 2:
                offset = data.split('`')[2]
            payments_controller.send_list_payments(travel_id, self.bot, id, call.message.message_id, offset)
        elif name == 'createpayment':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            msg = self.bot.send_message(id, '✏️ Придумайте название траты', reply_markup=
            create_cancel_keyboard('payments'))
            self.bot.register_next_step_handler(msg, self.enter_title_payment)
            user_manager.set_payload(id, travel_id)
        elif name == 'cancel':
            self.bot.clear_step_handler_by_chat_id(id)
            payload_object = user_manager.get_payload(id)
            payload = []
            if payload_object is not None:
                payload = user_manager.get_payload(id).split('`')

            if len(payload) >= 2:
                try:
                    travel_id = payload[0]
                    payment_id = payload[1]
                    self.handle(f'manager`{travel_id}', id, call)
                    db_payments.remove_payment(travel_id, payment_id)
                    return
                except:
                    pass
            elif len(payload) == 1:
                travel_id = payload[0]
                self.handle(f'manager`{travel_id}', id, call)
                return
            self.bot.edit_message_text('✅ Отменено', id, call.message.message_id)
        elif name == 'showaddinguser':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            payment_id = data.split('`')[2]

            users = db_payments.get_users_in_payment(travel_id, payment_id)
            markup_inline = types.InlineKeyboardMarkup()

            for i in range(len(users)):
                username = db_dict.get_username_from_id(users[i][0])
                markup_inline.add(
                    types.InlineKeyboardButton(text=f'{username} | {users[i][1]}₽',
                                               callback_data=f'payments_removefromlist`{travel_id}`{payment_id}`{users[i][0]}'))

            markup_inline.add(
                types.InlineKeyboardButton(text=f'➕ Добавить пользователя',
                                           callback_data=f'payments_adduser`{travel_id}`{payment_id}`'))
            markup_inline.add(
                types.InlineKeyboardButton(text=f'✅ Продолжить',
                                           callback_data=f'payments_createpaymentfinish`{travel_id}`{payment_id}`'))

            if 'edit' in data:
                self.bot.edit_message_text(f"📎 Теперь давай определимся, кого добавлять в эту трату", id,
                                           call.message.message_id,
                                           reply_markup=markup_inline)
            else:
                self.bot.send_message(id, f"📎 Теперь давай определимся, кого добавлять в эту трату",
                                      reply_markup=markup_inline)
        elif name == 'removefromlist':
            travel_id = data.split('`')[1]
            payment_id = data.split('`')[2]
            debtor_id = data.split('`')[3]

            db_payments.remove_from_payment_info(travel_id, payment_id, debtor_id)
            self.handle(f'showaddinguser`{travel_id}`{payment_id}`edit', id, call)
        elif name == 'adduser':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            payment_id = data.split('`')[2]

            users = db_payments.get_users_in_payment(travel_id, payment_id)
            travel_users = db_invite_friend.get_all_ids(travel_id)
            owner_id = int(travel_id.split('_')[0])

            if owner_id != call.from_user.id:
                travel_users.append(owner_id)

            markup_inline = types.InlineKeyboardMarkup()
            if len(travel_users) == 0:
                markup_inline.add(
                    types.InlineKeyboardButton(text=f'🔙 Назад',
                                               callback_data=f'payments_showaddinguser`{travel_id}`{payment_id}`edit'))
                self.bot.send_message(id, "‼️ В данном путешествии нет пользователей", reply_markup=markup_inline)
                return

            for user in travel_users:
                if user != call.from_user.id:
                    well = True
                    for j in users:
                        if user in j:
                            well = False
                    if well:
                        username = db_dict.get_username_from_id(user)
                        markup_inline.add(
                            types.InlineKeyboardButton(text=f'{username}',
                                                       callback_data=f'payments_adduser2`{travel_id}`{payment_id}`{user}'))
            markup_inline.add(
                types.InlineKeyboardButton(text=f'🔙 Назад',
                                           callback_data=f'payments_showaddinguser`{travel_id}`{payment_id}`edit'))

            self.bot.edit_message_text("Какому пользователю выставим счёт?", id, call.message.message_id,
                                       reply_markup=markup_inline)
        elif name == 'adduser2':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            payment_id = data.split('`')[2]
            debtor_id = data.split('`')[3]

            user_manager.set_payload(id, f"{travel_id}`{payment_id}`{debtor_id}")
            msg = self.bot.send_message(id, "✏️ Сколько должен пользователь?")
            self.bot.register_next_step_handler(msg, self.enter_amount_to_payment_info)
        elif name == 'createpaymentfinish':
            self.bot.clear_step_handler_by_chat_id(id)
            user_manager.set_payload(id, '')
            travel_id = data.split('`')[1]
            payment_id = data.split('`')[2]
            users = db_payments.get_users_in_payment(travel_id, payment_id)

            title = db_payments.get_payment_info(travel_id, payment_id)[0]
            travel_title = db_travel.get_information(travel_id)[1]
            for user in users:
                self.bot.send_message(user[0], f'🔔 Вас добавили в трату <b>"{title}"</b>, в путешествии "<b>{travel_title}</b>"\nВаш долг: <b>{user[1]}₽</b>',
                                      parse_mode='html')
            self.handle(f'open`{travel_id}`{payment_id}', id, call)
        elif name == 'open':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            payment_id = data.split('`')[2]

            payment_info = db_payments.get_payment_info(travel_id, payment_id)
            users_in_payment = db_payments.get_users_in_payment(travel_id, payment_id)
            username_owner = db_dict.get_username_from_id(payment_info[3])
            markup_inline = types.InlineKeyboardMarkup()
            for user_in_payment in users_in_payment:
                username = db_dict.get_username_from_id(user_in_payment[0])
                markup_inline.add(
                    types.InlineKeyboardButton(text=f'{username} | {user_in_payment[1]}₽',
                                               callback_data=f'payments_fullinfo`{travel_id}`{payment_id}`{user_in_payment[0]}'))
            markup_inline.add(
                types.InlineKeyboardButton(text=f'🔙 Назад',
                                           callback_data=f'payments_listpayments`{travel_id}'))

            added_text = ''
            if len(users_in_payment) > 0:
                added_text = '\n\nСписок участников траты 👇'
            self.bot.edit_message_text(
                f"<b>{payment_info[0]}</b>\nДата траты: <b>{payment_info[1]}</b>\nСумма: <b>{payment_info[2]}</b>\nСоздатель траты: @{username_owner}{added_text}",
                id, call.message.message_id, parse_mode='html', reply_markup=markup_inline)
        elif name == 'fullinfo':
            self.bot.clear_step_handler_by_chat_id(id)
            travel_id = data.split('`')[1]
            payment_id = data.split('`')[2]
            debtor_id = data.split('`')[3]

            payment_info = db_payments.get_payment_info(travel_id, payment_id)
            owner_id = payment_info[3]
            debtor_info = db_payments.get_user_payment_info(travel_id, payment_id, debtor_id)

            markup_inline = types.InlineKeyboardMarkup()
            if owner_id == call.from_user.id and int(debtor_info[1]) == 0:
                markup_inline.add(
                    types.InlineKeyboardButton(text=f'✅ Закрыть долг',
                                               callback_data=f'payments_closedebtor`{travel_id}`{payment_id}`{debtor_info[2]}'))
            markup_inline.add(
                types.InlineKeyboardButton(text=f'🔙 Назад',
                                           callback_data=f'payments_open`{travel_id}`{payment_id}'))
            status = "открыт"
            if int(debtor_info[1]) == 1:
                status = 'закрыт'
            self.bot.edit_message_text(f"Сумма долга: <b>{debtor_info[0]}₽</b>\nСтатус долга: <b>{status}</b>", id,
                                       call.message.message_id, reply_markup=markup_inline, parse_mode='html')
        elif name == 'closedebtor':
            travel_id = data.split('`')[1]
            payment_id = data.split('`')[2]
            debtor_id = data.split('`')[3]

            db_payments.update_payment_info(travel_id, payment_id, debtor_id, 'status', 1, False)
            self.handle(f'fullinfo`{travel_id}`{payment_id}`{debtor_id}', id, call)

    def enter_amount_to_payment_info(self, message: Message):
        payload = user_manager.get_payload(message.from_user.id).split('`')

        travel_id = payload[0]
        payment_id = payload[1]
        debtor_id = payload[2]

        if not is_float(message.text):
            msg = self.bot.send_message(message.from_user.id,
                                        "❌ Необходимо ввести число, без букв. Давай попробуем ещё раз", reply_markup=
                                        create_cancel_keyboard('payments'))
            self.bot.register_next_step_handler(msg, self.enter_amount_to_payment_info)
            return
        if float(message.text) <= 0:
            msg = self.bot.send_message(message.from_user.id,
                                        "❌ Число не может быть отрицательным или равняться нулю", reply_markup=
                                        create_cancel_keyboard('payments'))
            self.bot.register_next_step_handler(msg, self.enter_amount_to_payment_info)
            return
        if not db_payments.is_well_amount(message.text, travel_id, payment_id):
            msg = self.bot.send_message(message.from_user.id,
                                        "❌ С этим числом, сумма оперций будет больше суммы траты. Так не получится :(",
                                        reply_markup=
                                        create_cancel_keyboard('payments'))
            self.bot.register_next_step_handler(msg, self.enter_amount_to_payment_info)
            return
        db_payments.create_payment_info(travel_id, payment_id, debtor_id, message.text)
        self.handle(f'showaddinguser`{travel_id}`{payment_id}', message.from_user.id, None)

    def enter_title_payment(self, message: Message):
        travel_id = user_manager.get_payload(message.from_user.id)
        if message.text is None:
            msg = self.bot.send_message(message.from_user.id,'❌ Текст не может быть пустым, давай попробуем ещё раз',
                                        reply_markup=
                                        create_cancel_keyboard('payments'))
            self.bot.register_next_step_handler(msg, self.enter_title_payment)
            return
        if len(message.text) > 50:
            msg = self.bot.send_message(message.from_user.id,'❌ Название траты слишком длинное, пожалуйста подумай как можно его сократить',
                                     reply_markup=
                                        create_cancel_keyboard('payments'))
            self.bot.register_next_step_handler(msg, self.enter_title_payment)
            return

        payment_id = db_payments.create_payment(travel_id, message.from_user.id)
        user_manager.set_payload(message.from_user.id, f"{travel_id}`{payment_id}")
        db_payments.update_param(travel_id, payment_id, "title", message.text, True)

        msg = self.bot.send_message(message.from_user.id,
                                    '✏️ Когда была совершена трата?\n\nВведи дату платежа в формате день.месяц.год, например: 16.06.2024',
                                    reply_markup=create_cancel_keyboard('payments'))
        self.bot.register_next_step_handler(msg, self.enter_data_payment)

    def _check_data(self, text):
        if text is None:
            return False
        nodes = text.split('.')
        if len(nodes) != 3:
            return False
        if not (is_int(nodes[0]) and is_int(nodes[1]) and is_int(nodes[2])):
            return False
        day = int(nodes[0])
        month = int(nodes[1])
        year = int(nodes[2])

        if month > 12 or month < 1:
            return False
        if day > 31 or day < 1:
            return False
        if year < 2024:
            return False
        try:
            d = date(year, month, day)
        except:
            return False

        return True

    def enter_data_payment(self, message: Message):
        if not self._check_data(message.text):
            msg = self.bot.send_message(
                message.from_user.id,
                '❌ Дата не правильная :(\n\nВведи дату платежа в формате день.месяц.год, например: 16.06.2024',
                reply_markup=create_cancel_keyboard('payments'))
            self.bot.register_next_step_handler(msg, self.enter_data_payment)
            return
        payload = user_manager.get_payload(message.from_user.id).split('`')

        travel_id = payload[0]
        payment_id = payload[1]

        db_payments.update_param(travel_id, payment_id, "date", message.text, True)
        msg = self.bot.send_message(message.from_user.id,
                                    '✏️ Теперь необходимо указать сумму траты',
                                    reply_markup=create_cancel_keyboard('payments'))
        self.bot.register_next_step_handler(msg, self.enter_amount_payment)

    def enter_amount_payment(self, message: Message):
        if not is_float(message.text):
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Необходимо указать число, без каких-либо знаков. Давай попробуем ещё раз',
                                        reply_markup=create_cancel_keyboard('payments'))
            self.bot.register_next_step_handler(msg, self.enter_amount_payment)
            return
        if float(message.text) <= 0:
            msg = self.bot.send_message(message.from_user.id,
                                        '❌ Число не может быть отрицательным или равняться нулю',
                                        reply_markup=create_cancel_keyboard('payments'))
            self.bot.register_next_step_handler(msg, self.enter_amount_payment)
            return
        payload = user_manager.get_payload(message.from_user.id).split('`')
        travel_id = payload[0]
        payment_id = payload[1]

        db_payments.update_param(travel_id, payment_id, "amount", round(float(message.text), 2), False)
        users = db_payments.get_users_in_payment(travel_id, payment_id)
        markup_inline = types.InlineKeyboardMarkup()

        for i in range(len(users)):
            username = db_dict.get_username_from_id(users[i][0])
            markup_inline.add(
                types.InlineKeyboardButton(text=f'{username} | {users[i][1]}₽',
                                           callback_data=f'payments_removefromlist`{travel_id}`{payment_id}`{users[i][0]}'))

        markup_inline.add(
            types.InlineKeyboardButton(text=f'➕ Добавить пользователя',
                                       callback_data=f'payments_adduser`{travel_id}`{payment_id}`'))
        markup_inline.add(
            types.InlineKeyboardButton(text=f'✅ Продолжить',
                                       callback_data=f'payments_createpaymentfinish`{travel_id}`{payment_id}`'))

        self.bot.send_message(message.from_user.id, f"📎 Теперь давай определимся, кого добавлять в эту трату",
                              reply_markup=markup_inline)
