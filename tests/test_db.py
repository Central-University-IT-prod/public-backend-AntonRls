import unittest

import utils
from DB import db_user, db_dict, db_manager, db_user_full_info, db_travel, db_places, db_payments, db_notes, \
    db_invite_friend, db_locations, db_guide


def _init_base():
    db_manager.set_test()
    db_manager.create_database()


class TestDB(unittest.TestCase):

    def test_register(self):
        _init_base()

        self.assertEqual(db_user.is_new_user(-100), True, 'Должно быть True')
        self.assertEqual(db_dict.get_username_from_id(-100), None, 'Должно вернуться None')
        db_user.register_user(-100, "testuser")
        self.assertEqual(db_user.is_new_user(-100), False, 'Должно быть False ')
        self.assertEqual(db_dict.get_username_from_id(-100), 'testuser', 'Должен вернуться testuser')

    def test_update_user_info(self):
        _init_base()
        if db_user.is_new_user(-100):
            db_user.register_user(-100, 'testuser')
        db_user.update_param_from_userid('Users', 'age', 25, -100, False)
        db_user.update_param_from_userid('Users', 'bio', "*_#/₽/\\ \"@!a", -100, False)
        self.assertEqual(db_user.get_value_from_user_id('Users', -100, 'age'), 25, 'Некорректный возраст')
        self.assertEqual(db_user.get_info_user(-100), (25, None, None, "*_#/₽/\\ \"@!a"),
                         'Неверно возращается информация о пользователе')

    def test_register_full_info(self):
        _init_base()

        message_error = 'Неверное получение full info'
        self.assertEqual(db_user_full_info.get_info(-100), None, message_error)
        db_user_full_info.add_info(-100)
        self.assertEqual(db_user_full_info.get_info(-100), (None, None), message_error)
        interests = 'машины, спорт'
        db_user_full_info.update_param(-100, 'interests', interests, True)
        self.assertEqual(db_user_full_info.get_param(-100, 'interests'), interests, message_error)
        self.assertEqual(db_user_full_info.get_info(-100), (None, interests), message_error)

    def test_create_travel(self):
        _init_base()

        travel_id = db_travel.create_travel(-100, 'test_title')
        self.assertEqual(db_travel.get_information(travel_id), (travel_id, 'test_title', None), 'Неверное значение '
                                                                                                'get travel info')
        return travel_id

    def test_list_travel(self):
        self.test_create_travel()
        self.assertEqual(len(db_travel.get_travel_list(-100)), 2, 'Неверное полуение travel_list')

    def test_remove_travel(self):
        travel_id = self.test_create_travel()

        db_travel.remove_travel(-100, travel_id)
        self.assertEqual(len(db_travel.get_travel_list(-100)), 0, 'Неверное удаление путешествия')

    def test_update_travel_parm(self):
        travel_id = self.test_create_travel()
        description = "test description"
        db_travel.update_travel_parm(-100, travel_id, 'description', description)
        self.assertEqual(db_travel.get_information(travel_id), (travel_id, 'test_title', description),
                         'Неверное обновление параметров в путешествии')

    def test_places(self):
        _init_base()

        db_places.add_place(-100, -1)
        db_places.update_place_info(-100, 'city_id', -2)
        self.assertEqual(db_places.get_city_id(-100), -2, 'Неверная работа db_places')

    def test_payments(self):
        _init_base()

        travel_id = '-100_1'
        payment_title = 'payment title'

        payment_id = db_payments.create_payment(travel_id, -100)
        db_payments.update_param(travel_id, payment_id, 'title', payment_title, True)
        self.assertEqual(db_payments.get_payment_info(travel_id, payment_id), (payment_title, None, None, -100),
                         'Неверная работа db_payments')
        db_payments.create_payment_info(travel_id, payment_id, -99, 10)
        self.assertEqual(db_payments.get_user_payment_info(travel_id, payment_id, -99), (10.0, 0, -99),
                         'Неверная работа db_payments info')
        self.assertEqual(db_payments.i_debtors(travel_id, -99), {None: 10.0}, 'Неверная работа db_payments')
        self.assertEqual(db_payments.i_debtors(travel_id, -100), {}, 'Неверная работа db_payments')
        self.assertEqual(db_payments.my_debtors(travel_id, -100), {None: 10.0}, 'Неверная работа db_payments')

    def test_notes(self):
        _init_base()

        travel_id = '-100_1'
        title = 'test note'
        description = 'test description'

        note_id = db_notes.create_note(travel_id, title)
        self.assertEqual(db_notes.get_note_info(travel_id, note_id), [None, None, 1], 'Неверная работа db_notes')
        db_notes.update_param_note(travel_id, note_id, 'description', description)
        self.assertEqual(db_notes.get_note_info(travel_id, note_id), [description, None, 1], 'Неверная работа db_notes')
        db_notes.update_param_note(travel_id, note_id, 'is_public', '0')
        self.assertEqual(db_notes.get_notes(travel_id, -99), [], 'Неверная работа db_notes')
        self.assertEqual(db_notes.get_notes(travel_id, -100), [('0', title, 1)], 'Неверная работа db_notes')
        db_notes.remove_note(travel_id, note_id)
        self.assertEqual(db_notes.get_note_info(travel_id, note_id), None, 'Неверная работа db_notes')

    def test_invite_friend(self):
        _init_base()

        travel_id = '-100_1'
        self.assertEqual(db_invite_friend.get_all_ids(travel_id), [], 'Неверная работа db_invite_friend')
        db_invite_friend.insert_invite(travel_id, -100)
        self.assertEqual(db_invite_friend.get_all_ids(travel_id), [-100], 'Неверная работа db_invite_friend')
        self.assertEqual(db_invite_friend.get_travel_ids(-100), [travel_id], 'Неверная работа db_invite_friend')
        self.assertEqual(db_invite_friend.is_new_user(-100, travel_id), False, 'Неверная работа db_invite_friend')
        db_invite_friend.remove_user(-100, travel_id)
        self.assertEqual(db_invite_friend.get_travel_ids(-100), [], 'Неверная работа db_invite_friend')

    def test_locations(self):
        _init_base()

        travel_id = '-100_1'

        id_location = db_locations.create_location(travel_id, 'Россия, Москва', -1)
        id_location_2 = db_locations.create_location(travel_id, 'Россия, Воронеж', -2)
        self.assertEqual(db_locations.get_location_information(travel_id, id_location),
                         ('-100_1', 'Россия, Москва', -1, None, None, 1), 'Неверная работа db_locations')
        db_locations.update_param(travel_id, id_location, 'start_date', '16.06.2024', True)
        db_locations.update_param(travel_id, id_location_2, 'start_date', '15.06.2024', True)
        self.assertEqual(db_locations.get_location_information(travel_id, id_location),
                         ('-100_1', 'Россия, Москва', -1, '16.06.2024', None, 1), 'Неверная работа db_locations')
        self.assertEqual(db_locations.get_information(travel_id),
                         [('-100_1', 'Россия, Воронеж', -2, '15.06.2024', None, 2),
                          ('-100_1', 'Россия, Москва', -1, '16.06.2024', None, 1)], 'Неверная работа db_locations')

        self.assertEqual(db_locations.data_is_empty(travel_id, utils.to_unix_time('16.06.2024')), False,
                         'Неверная работа db_locations')
        self.assertEqual(db_locations.data_is_empty(travel_id, utils.to_unix_time('16.06.2025')), True,
                         'Неверная работа db_locations')
        self.assertEqual(db_locations.data_is_empty(travel_id, utils.to_unix_time('17.06.2024')), True,
                         'Неверная работа db_locations')
        self.assertEqual(db_locations.data_is_empty_interval(travel_id, utils.to_unix_time('15.06.2024'),
                                                             utils.to_unix_time('18.06.2024')), False,
                         'Неверная работа db_locations')
        self.assertEqual(db_locations.data_is_empty_interval(travel_id, utils.to_unix_time('15.06.2025'),
                                                             utils.to_unix_time('18.06.2025')), True,
                         'Неверная работа db_locations')
        db_locations.remove_location(travel_id, id_location_2)
        self.assertEqual(db_locations.get_information(travel_id),
                         [('-100_1', 'Россия, Москва', -1, '16.06.2024', None, 1)], 'Неверная работа db_locations')

    def test_guide(self):
        _init_base()

        db_guide.add_guide(-100, 'test2')
        self.assertEqual(db_guide.user_not_have_guide(-100, 'test'), True, 'Неверная работа db_guide')
        self.assertEqual(db_guide.user_not_have_guide(-100, 'test2'), False, 'Неверная работа db_guide')


if __name__ == '__main__':
    unittest.main()
