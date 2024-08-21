import math
import time

from DB import db_invite_friend
from DB.db_manager import commit, create_connection

import utils


def create_travel(user_id, title):
    connection = create_connection()
    cursor = connection.cursor()

    travel_id = f"{user_id}_{math.ceil(time.time())}"
    cursor.execute(f'''
        INSERT INTO Traveles (user_id, title, travel_id) VALUES ({user_id}, (?), "{travel_id}")
    ''', (title,))
    commit(connection)
    return travel_id


def update_travel_parm(user_id, travel_id, name_parm, value_parm):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
        UPDATE Traveles SET {name_parm}=(?) WHERE user_id = {user_id} AND travel_id="{travel_id}"
    ''', (value_parm,))
    commit(connection)


def get_travel_list(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
            select travel_id, title from Traveles where user_id = {user_id}
        ''')
    travelles = cursor.fetchall()

    travel_listid = db_invite_friend.get_travel_ids(user_id)
    for id in travel_listid:
        cursor.execute(f'''
            select travel_id, title from Traveles where travel_id="{id}"
        ''')
        travelles.append(cursor.fetchone())
    commit(connection)
    return travelles


def remove_travel(user_id, travel_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
                 DELETE from Traveles where travel_id="{travel_id}" AND user_id={user_id}
            ''')
    commit(connection)


def get_count_day_in_travel(travel_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
                        select start_date,end_date from Locations where travel_id="{travel_id}"
                ''')
    days = cursor.fetchall()
    commit(connection)
    if len(days) == 0:
        return 0
    minunix = 0
    maxunix = 0

    for location in days:
        start_unix = utils.to_unix_time(location[0])
        if start_unix < minunix or minunix == 0:
            minunix = start_unix
        if start_unix > maxunix and start_unix != minunix:
            maxunix = start_unix
        if location[1] is not None:
            end_unix = utils.to_unix_time(location[1])
            if end_unix > maxunix or maxunix == 0:
                maxunix = end_unix
    if maxunix == 0:
        return 1

    return round((maxunix - minunix) / 86400)


def get_information(travel_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute('''
                SELECT title, description FROM Traveles WHERE travel_id="{0}"
            '''.format(travel_id))
    info = cursor.fetchone()
    commit(connection)
    if info is None:
        return None
    return travel_id, info[0], info[1]
