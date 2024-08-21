from telebot import TeleBot, types

from Controllers import guide_controller
from DB import db_user, db_user_full_info, db_guide


def send_profile_info(user_id, bot: TeleBot, message_id=0):
    if db_guide.user_not_have_guide(user_id, 'profile'):
        guide_controller.show_guide(bot, user_id,
                                    'profile',
                                    'ℹ️ В данном разделе находится информация о твоём профиле. Советую указать твои интересы, а так-же пол, эта информация будет использоваться при поиске компаньонов в путешествии',
                                    'profile_showprofile')
        return

    info_user = db_user.get_info_user(user_id)
    info_full_user = db_user_full_info.get_info(user_id)

    age = "не указан"
    if info_user[0] is not None:
        age = info_user[0]

    place = f"{info_user[1]}, {info_user[2]}"

    bio = info_user[3]
    gender = "не указан"
    if info_full_user[0] is not None:
        gender_num = int(info_full_user[0])
        if gender_num == 1:
            gender = "мужской"
        elif gender_num == 2:
            gender = "женский"
    interests = "не указаны"
    if info_full_user[1] is not None:
        if info_full_user[1].strip() != '':
            interests = info_full_user[1]

    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.add(types.InlineKeyboardButton(text='📝 Изменить возраст', callback_data=f'profile_editage'),
                      types.InlineKeyboardButton(text='📝 Изменить адрес', callback_data=f'profile_editplace'))
    markup_inline.add(types.InlineKeyboardButton(text='📝 Изменить пол', callback_data=f'profile_editgender'),
                      types.InlineKeyboardButton(text='📝 Изменить интересы', callback_data=f'profile_editinterests'))
    markup_inline.add(types.InlineKeyboardButton(text='📝 Изменить описание', callback_data=f'profile_editbio'))
    if message_id == 0:
        bot.send_message(user_id,
                     f"<b>🚇 Ваш профиль</b>\n\nВозраст: <b>{age}</b>\nАдрес: <b>{place}</b>\nПол: <b>{gender}</b>\nИнтересы: <b>{interests}</b>\nОписание: <b>{bio}</b>",
                     parse_mode="html", reply_markup=markup_inline)
    else:
        bot.edit_message_text(f"<b>🚇 Ваш профиль</b>\n\nВозраст: <b>{age}</b>\nАдрес: <b>{place}</b>\nПол: <b>{gender}</b>\nИнтересы: <b>{interests}</b>\nОписание: <b>{bio}</b>",
                     user_id, message_id, parse_mode="html", reply_markup=markup_inline)


def search_users(user_id, bot: TeleBot, offset, travel_id, message_id):
    users = db_user.search_users(user_id, travel_id)

    if len(users) == 0 or offset >= len(users):
        markup_inline = types.InlineKeyboardMarkup()
        markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                     callback_data=f'travel_control`{travel_id}`edit'))
        bot.edit_message_text("К сожалению, пока что я не могу найти подходящих вам людей 😔\n\nПопробуйте изменить свои интересы в разделе \"📱 Мой профиль\" ", user_id, message_id, reply_markup=markup_inline)
        return
    markup_inline = types.InlineKeyboardMarkup()

    if offset == 0 and offset + 1 < len(users):
        markup_inline.add(
            types.InlineKeyboardButton(text='➡️',
                                       callback_data=f'profile_search`{travel_id}`1')
        )

    elif offset + 1 < len(users) and offset > 0:
        markup_inline.add(

            types.InlineKeyboardButton(text='⬅️',
                                       callback_data=f'profile_search`{travel_id}`{offset - 1}'),
            types.InlineKeyboardButton(text='➡️',
                                       callback_data=f'profile_search`{travel_id}`{offset + 1}'),
            row_width=2)
    elif offset + 1 == len(users) and len(users) != 1:
        markup_inline.add(
                          types.InlineKeyboardButton(text='⬅️',
                                                     callback_data=f'profile_search`{travel_id}`{offset - 1}'))
    markup_inline.add(types.InlineKeyboardButton(text='🔙 Назад',
                                                 callback_data=f'travel_control`{travel_id}`edit'))

    gender = 'не указан'
    if users[offset][4] is not None:
        if int(users[offset][4]) == 1:
            gender = 'мужской'
        elif int(users[offset][4]) == 2:
            gender = 'женский'
    bot.edit_message_text(
        f"@{users[offset][6]}\n\nВозраст: <b>{users[offset][0]}</b>\nАдрес: <b>{users[offset][1]}, {users[offset][2]}</b>\nПол: <b>{gender}</b>\nИнтересы: <b>{users[offset][5]}</b>\nОписание:\n<b>{users[offset][3]}</b>",
        user_id, message_id, reply_markup=markup_inline, parse_mode='html')
