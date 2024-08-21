from DB.db_manager import commit, create_connection
from DB import db_user


def add_to_exchange(travel_id, username, user_id):
    age = int(db_user.get_value_from_user_id('Users', user_id, 'age'))
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
    insert into SearchExchange (travel_id, username, age) values ("{travel_id}", "{username}", {age})
    ''')
    commit(connection)


def travel_in_exchange(travel_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
        select * from SearchExchange where travel_id="{travel_id}"
        ''')
    info = cursor.fetchone()
    commit(connection)

    return info is not None


def remove_travel_from_exchange(travel_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
            delete from SearchExchange where travel_id="{travel_id}"
            ''')
    commit(connection)


def get_list_exchange():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
                select travel_id from SearchExchange
                ''')

    items = cursor.fetchall()[::-1]
    result = []
    for item in items:
        cursor.execute(f'select title from Traveles where travel_id="{item[0]}"')
        title = cursor.fetchone()[0]
        result.append((title, item[0]))
    commit(connection)
    return result
