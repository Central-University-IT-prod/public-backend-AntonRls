from DB.db_manager import commit, create_connection


def _get_note_id(travel_id) -> int:
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
          select note_id from Notes where travel_id="{travel_id}"
    ''')
    ids = cursor.fetchall()
    result = 1
    for i in ids:
        if int(i[0]) >= result:
            result = int(i[0]) + 1
    commit(connection)

    return result


def update_param_note(travel_id, note_id, param_name, param_value):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
        update Notes set {param_name}=(?) where travel_id="{travel_id}" and note_id={note_id}
        ''', (param_value,))
    commit(connection)


def remove_note(travel_id, note_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
        delete from Notes where note_id={note_id} and travel_id="{travel_id}"            
    ''')
    cursor.execute(f'''
            delete from NotesInfo where note_id={note_id} and travel_id="{travel_id}"            
        ''')
    commit(connection)


def create_note(travel_id, title) -> int:
    note_id = _get_note_id(travel_id)
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
        insert into Notes (travel_id, title, note_id, is_public) values ("{travel_id}", (?), {note_id}, "1")
        ''', (title,))

    commit(connection)
    return note_id


def get_note_info(travel_id, note_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
            select description, is_public from Notes where travel_id="{travel_id}" and note_id={note_id}
        ''')
    info = cursor.fetchone()
    if info is None:
        return None
    description = info[0]
    is_public = int(info[1])
    cursor.execute(f'''
                select url from NotesInfo where travel_id="{travel_id}" and note_id={note_id}
            ''')
    url_maybe = cursor.fetchone()
    url = None
    if url_maybe is not None:
        url = url_maybe[0]
    result = [description, url, is_public]
    commit(connection)
    return result


def get_notes(travel_id, user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
            select is_public, title, note_id from Notes where travel_id="{travel_id}"
        ''')
    notes = cursor.fetchall()
    commit(connection)

    result = []
    for note in notes:
        if int(note[0]) == 1:
            result.append(note)
        elif travel_id.split('_')[0] == str(user_id):
            result.append(note)
    return result


def create_url_note(url, travel_id, note_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'''
            insert into NotesInfo (travel_id, url, note_id) values ("{travel_id}", "{url}", {note_id})
        ''')

    commit(connection)
