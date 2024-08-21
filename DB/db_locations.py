import math
import time
from datetime import date

from DB.db_manager import commit, create_connection

import utils


def get_id_location(travel_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'SELECT location_id from Locations where travel_id="{travel_id}"')
    ids = cursor.fetchall()

    result = 1
    for location_id in ids:
        if int(location_id[0]) >= result:
            result = int(location_id[0]) + 1
    commit(connection)
    return result


def create_location(travel_id, location_name, place_id):
    connection = create_connection()
    cursor = connection.cursor()
    location_id = get_id_location(travel_id)
    cursor.execute(f'''
        insert into Locations (travel_id, location_name, place_id, location_id) values ("{travel_id}", "{location_name}", {place_id}, {location_id})
    ''')

    commit(connection)
    return location_id


def remove_location(travel_id, location_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
            DELETE from Locations where travel_id="{travel_id}" AND location_id={location_id}
        ''')

    commit(connection)


def update_param(travel_id, location_id, parm_name, parm_value, is_string=True):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''update Locations set {parm_name}=(?) where travel_id="{travel_id}" AND location_id={location_id}
                        ''', (parm_value,))
    commit(connection)


def data_is_empty(travel_id, unixtimedata, location_id=0):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
        select start_date, end_date, location_id from Locations where travel_id="{travel_id}"
    ''')
    datas = cursor.fetchall()
    for data in datas:
        if data[2] != location_id and not (data[0] is None) and (data[0].strip() != '') and not (data[1] is None) and (
                data[1].strip() != ''):
            data1 = date(int(data[0].split('.')[2]), int(data[0].split('.')[1]), int(data[0].split('.')[0]))
            data2 = date(int(data[1].split('.')[2]), int(data[1].split('.')[1]), int(data[1].split('.')[0]))

            unix1 = time.mktime(data1.timetuple())
            unix2 = time.mktime(data2.timetuple())
            if unix1 <= unixtimedata <= unix2:
                return False
        elif data[2] != location_id and not data[0] is None and data[0].strip() != '':
            data1 = date(int(data[0].split('.')[2]), int(data[0].split('.')[1]), int(data[0].split('.')[0]))
            unix1 = time.mktime(data1.timetuple())
            if unix1 == unixtimedata:
                return False
    commit(connection)
    return True


def data_is_empty_interval(travel_id, unixtimedata, unixtimedata2, location_id=0):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
            select start_date, end_date, location_id from Locations where travel_id="{travel_id}"
        ''')
    datas = cursor.fetchall()
    days = math.ceil((unixtimedata2 - unixtimedata) / 86400)
    for i in range(1, days):
        for data in datas:
            if data[2] != location_id and not (data[0] is None) and (data[0].strip() != '') and not (
                    data[1] is None) and (data[1].strip() != ''):
                data1 = date(int(data[0].split('.')[2]), int(data[0].split('.')[1]), int(data[0].split('.')[0]))
                data2 = date(int(data[1].split('.')[2]), int(data[1].split('.')[1]), int(data[1].split('.')[0]))

                unix1 = time.mktime(data1.timetuple())
                unix2 = time.mktime(data2.timetuple())
                if unix1 <= unixtimedata + i * 86400 <= unix2:
                    return False
            elif data[2] != location_id and not data[0] is None and data[0].strip() != '':
                data1 = date(int(data[0].split('.')[2]), int(data[0].split('.')[1]), int(data[0].split('.')[0]))
                unix1 = time.mktime(data1.timetuple())
                if unix1 == unixtimedata + i * 86400:
                    return False
    commit(connection)
    return True


def _sort_location(locations):
    good = True
    while good:
        good = False
        for i in range(len(locations) - 1):
            unix_this = utils.to_unix_time(locations[i][3])
            unix_will = utils.to_unix_time(locations[i+1][3])
            if unix_this > unix_will:
                temp = locations[i+1]
                locations[i+1] = locations[i]
                locations[i] = temp
                good = True
    return locations


def get_information(travel_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
                select travel_id,location_name,place_id,start_date,end_date,location_id from Locations where travel_id="{travel_id}"
            ''')
    locations = cursor.fetchall()

    return _sort_location(locations)


def get_location_information(travel_id, location_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
                select travel_id,location_name,place_id,start_date,end_date,location_id from Locations where travel_id="{travel_id}" and location_id={location_id}
            ''')
    locations = cursor.fetchone()
    return locations
