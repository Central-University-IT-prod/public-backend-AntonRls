from DB.db_manager import commit, create_connection
from DB import db_dict, db_invite_friend


def is_new_user(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM UsersDict WHERE user_id=' + str(user_id))
    users = cursor.fetchall()
    connection.close()
    return len(users) == 0


def update_param_from_userid(table_name, parm_name, value, user_id, is_string):
    connection = create_connection()
    cursor = connection.cursor()
    new_value = value

    cursor.execute(f'''
        UPDATE {table_name} SET {parm_name}=(?) WHERE user_id={user_id} 
    ''', (new_value,))
    commit(connection)


def get_value_from_user_id(table_name, user_id, parm_name):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
        SELECT {parm_name} FROM {table_name} WHERE user_id={user_id}
    ''')
    result = cursor.fetchone()[0]
    connection.close()
    return result


def get_info_user(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
            SELECT age, country, city, bio FROM Users WHERE user_id={user_id}
        ''')
    result = cursor.fetchone()
    connection.close()
    return result


def search_users(user_id, travel_id):
    connection = create_connection()
    cursor = connection.cursor()
    in_travel = db_invite_friend.get_all_ids(travel_id)
    cursor.execute(f'select age, country, city, bio from Users where user_id={user_id}')
    age = int(cursor.fetchone()[0])
    cursor.execute(f'select interests from UsersFullInfo where user_id={user_id}')
    interests_maybe = cursor.fetchone()

    if interests_maybe[0] is None:
        return []
    interests = interests_maybe[0].split(',')
    if len(interests) == 0:
        return []
    cursor.execute(f'select user_id from Users where age >= {age - 5} and age <= {age + 5}')
    users = cursor.fetchall()


    result_user_ids = []
    for user in users:

        cursor.execute(f'select user_id,interests from UsersFullInfo where user_id={user[0]}')

        maybe_id = cursor.fetchone()
        if maybe_id is not None and int(maybe_id[0]) != int(user_id) and maybe_id[1] is not None:
            well = False
            interests_user = maybe_id[1]
            for i in interests:
                if i.strip() in interests_user and i.strip() != '':
                    well = True
                    break
            if well and maybe_id[0] not in in_travel:
                result_user_ids.append(maybe_id[0])

    result = []
    for id in result_user_ids:

        cursor.execute(f'select gender, interests from UsersFullInfo where user_id={id}')
        info_full = cursor.fetchone()
        cursor.execute(f'select age, country, city, bio from Users where user_id={id}')
        info = cursor.fetchone()
        username = db_dict.get_username_from_id(id)
        result.append((info[0], info[1], info[2], info[3], info_full[0], info_full[1], username))
    commit(connection)
    return result[::-1]


def register_user(user_id, username):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
        INSERT INTO Users (user_id) VALUES ({user_id})
    ''')

    cursor.execute(f'''
        INSERT INTO UsersDict (user_id, username) VALUES ({user_id}, "{username}")
    ''')

    commit(connection)
