from DB.db_manager import commit, create_connection


def is_new_info(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f"select * from UsersFullInfo where user_id={user_id}")
    info = cursor.fetchone()
    commit(connection)

    return info is None


def add_info(user_id):
    if is_new_info(user_id):
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(f"insert into UsersFullInfo (user_id) values ({user_id})")
        commit(connection)


def update_param(user_id, param_name, param_value, is_string):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'update UsersFullInfo set {param_name}=(?) where user_id={user_id}', (param_value,))
    commit(connection)


def get_param(user_id, parm_name):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'select {parm_name} from UsersFullInfo where user_id={user_id}')
    result = cursor.fetchone()[0]
    commit(connection)
    return result


def get_info(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'select gender, interests from UsersFullInfo where user_id={user_id}')
    result = cursor.fetchone()
    commit(connection)
    return result
