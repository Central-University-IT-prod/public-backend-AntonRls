import unittest
import utils


class TestUtils(unittest.TestCase):
    def test_int(self):
        self.assertEqual(utils.is_int('.'), False, 'Неверная работа utils int')
        self.assertEqual(utils.is_int('1'), True, 'Неверная работа utils int')
        self.assertEqual(utils.is_int(''), False, 'Неверная работа utils int')
        self.assertEqual(utils.is_int(None), False, 'Неверная работа utils int')
        self.assertEqual(utils.is_int(1), True, 'Неверная работа utils int')
        self.assertEqual(utils.is_int(1.1), True, 'Неверная работа utils int')

    def test_float(self):
        self.assertEqual(utils.is_float('.'), False, 'Неверная работа utils float')
        self.assertEqual(utils.is_float('1'), True, 'Неверная работа utils float')
        self.assertEqual(utils.is_float(''), False, 'Неверная работа utils float')
        self.assertEqual(utils.is_float(None), False, 'Неверная работа utils float')
        self.assertEqual(utils.is_float(1), True, 'Неверная работа utils float')
        self.assertEqual(utils.is_float(1.1), True, 'Неверная работа utils float')

    def test_to_unix(self):
        self.assertEqual(utils.to_unix_time('16.06.2024'), 1718485200.0, 'Неверная работа utils to unix')

    def test_get_eng_name(self):
        self.assertEqual(utils.get_eng_name(10), 'october', 'Неверная работа utils get eng name')

    def test_get_rus_name(self):
        self.assertEqual(utils.get_rus_name(10), ['октябрь', 'октября'], 'Неверная работа utils get eng name')

    def test_get_rus_month_from_name(self):
        self.assertEqual(utils.get_rus_month_from_name('июнь'), 6, 'Неверная работа utils get rus month')

    def test_list_to_str(self):
        self.assertEqual(utils.list_to_str([1, 2, 3]), '1, 2, 3', 'Неверная работа list to str')
        self.assertEqual(utils.list_to_str(['1', '2', '3']), '1, 2, 3', 'Неверная работа list to str')

    def test_is_owner_travel(self):
        self.assertEqual(utils.is_owner_travel('100_1', 99), False, 'Неверная работа is owner travel')
        self.assertEqual(utils.is_owner_travel('100_1', 100), True, 'Неверная работа is owner travel')

    def test_decline_number(self):
        self.assertEqual(utils.decline_number(10), '10 дней', 'Неверная работа decline number')
        self.assertEqual(utils.decline_number(1), '1 день', 'Неверная работа decline number')
        self.assertEqual(utils.decline_number(32), '32 дня', 'Неверная работа decline number')


if __name__ == '__main__':
    unittest.main()
