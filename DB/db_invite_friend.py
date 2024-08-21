from DB.db_manager import commit, create_connection


def insert_invite(travel_id, user_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
            insert into FriendsInTravel (travel_id, user_id) values ("{travel_id}", {user_id})
        ''')
    commit(connection)


def get_travel_ids(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
                select travel_id from FriendsInTravel where user_id={user_id}
            ''')
    ids = cursor.fetchall()
    commit(connection)

    result = []
    for id in ids:
        result.append(id[0])
    return result


def remove_user(user_id, travel_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
                        delete from FriendsInTravel where user_id={user_id} and travel_id="{travel_id}"
                    ''')
    commit(connection)


def is_new_user(user_id, travel_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
                    select * from FriendsInTravel where user_id={user_id} and travel_id="{travel_id}"
                ''')
    ids = cursor.fetchall()
    commit(connection)
    return len(ids) == 0


def get_all_ids(travel_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
                    select user_id from FriendsInTravel where travel_id="{travel_id}"
                ''')
    ids = cursor.fetchall()
    commit(connection)

    result = []
    for id in ids:
        result.append(id[0])
    return result
