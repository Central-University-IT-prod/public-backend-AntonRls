from DB.db_manager import commit, create_connection


def get_user_from_username(username):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
        select user_id from UsersDict where username = "{username}"
    ''')
    user_id = cursor.fetchone()
    commit(connection)
    if user_id is None:
        return None

    return user_id[0]


def get_username_from_id(id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
            select username from UsersDict where user_id = {id}
        ''')
    user_name = cursor.fetchone()
    commit(connection)
    if user_name is None:
        return None

    return user_name[0]


def update_username(user_id, username):
    old_username = get_username_from_id(user_id)
    if old_username != user_id:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(f'''
                    update UsersDict set username="{username}" where user_id={user_id}
                ''')
        commit(connection)
