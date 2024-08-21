from DB.db_manager import commit, create_connection


def add_place(user_id, country_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
        INSERT INTO Places (user_id, country_id) VALUES ({user_id}, {country_id})
    ''')

    commit(connection)


def update_place_info(user_id, parm_name, parm_val):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute('''
        update Places set {0}={1} where user_id={2}
    '''.format(parm_name, parm_val, user_id))
    commit(connection)


def get_city_id(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
            select city_id from Places where user_id={user_id}
        ''')
    city_id = cursor.fetchone()[0]
    commit(connection)
    return city_id


def is_new_place_info(place_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'select * from PlacesInfo where place_id={place_id}')
    info = cursor.fetchall()
    commit(connection)
    return len(info) == 0


def add_place_info(place_id, lat, long):
    if not is_new_place_info(place_id):
        return
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'insert into PlacesInfo (place_id, lat, long) values ({place_id}, "{lat}", "{long}")')
    commit(connection)


def get_cord(place_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'select lat, long from PlacesInfo where place_id={place_id} ')
    info = cursor.fetchone()
    commit(connection)
    return info
