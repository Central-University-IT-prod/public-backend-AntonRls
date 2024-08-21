from DB.db_manager import commit, create_connection


def add_guide(user_id, guide_name):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'insert into GuideInfo (user_id, guide_name) values ({user_id},"{guide_name}")')

    commit(connection)


def user_not_have_guide(user_id, guide_name):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'select * from GuideInfo where user_id={user_id} and guide_name="{guide_name}"')
    info = cursor.fetchone()
    commit(connection)
    return info is None
