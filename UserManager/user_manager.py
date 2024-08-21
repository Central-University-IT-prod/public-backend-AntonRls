from DB import db_user


def set_payload(id, payload):
    db_user.update_param_from_userid('Users', 'payload', payload, id, True)


def get_payload(id):
    return db_user.get_value_from_user_id('Users', id, 'payload')
