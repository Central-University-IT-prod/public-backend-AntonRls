import time
from datetime import date


def is_int(value):
    if value is None:
        return False
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_float(value):
    if value is None:
        return False
    try:
        float(value)
        return True
    except ValueError:
        return False


eng_name_dict = {1: "january",
                 2: "february",
                 3: "march",
                 4: "april",
                 5: "may",
                 6: "june",
                 7: "july",
                 8: "august",
                 9: "september",
                 10: "october",
                 11: "november",
                 12: "december"}
rus_name_dict = {
    1: ["январь", "января"],
    2: ["февраль", "февраля"],
    3: ["март", "марта"],
    4: ["апрель", "апреля"],
    5: ["май", "мая"],
    6: ["июнь", "июня"],
    7: ["июль", "июля"],
    8: ["август", "августа"],
    9: ["сентябрь", "сентября"],
    10: ["октябрь", "октября"],
    11: ["ноябрь", "ноября"],
    12: ["декабрь", "декабря"]
}


def get_eng_name(month):
    global eng_name_dict
    return eng_name_dict[int(month)]


def get_rus_name(month):
    global rus_name_dict
    return rus_name_dict[int(month)]


def get_rus_month_from_name(name):
    global rus_name_dict
    values = list(rus_name_dict.values())
    for i in range(len(values)):
        if name in values[i]:
            return int(list(rus_name_dict.keys())[i])


def to_unix_time(str_date):
    days = int(str_date.split('.')[0])
    month = int(str_date.split('.')[1])
    years = int(str_date.split('.')[2])

    return time.mktime(date(years, month, days).timetuple())


def list_to_str(ar):
    result = ""
    for i in range(len(ar)):
        ar[i] = str(ar[i])
        if ar[i].strip() != '' and ar[i].strip() != 'None':
            result += f"{ar[i].strip()}"
            if i + 1 != len(ar):
                result += ", "
    return result


def is_owner_travel(travel_id, user_id):
    return int(travel_id.split('_')[0]) == int(user_id)


def decline_number(number):
    words = ['дней', 'день', 'дня']
    result = ""
    checker = number % 10
    if number == 0 or checker == 0 or checker >= 5 or number in range(11, 19):
        result = f"{number} {words[0]}"
    elif checker == 1:
        result = f"{number} {words[1]}"
    else:
        result += f"{number} {words[2]}"
    return result
