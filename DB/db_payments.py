from DB import db_dict
from DB.db_manager import commit, create_connection


def get_payment_id(travel_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'select payment_id from Payments where travel_id="{travel_id}"')
    ids = cursor.fetchall()
    result = 1
    for id in ids:
        if result <= int(id[0]):
            result = int(id[0]) + 1
    commit(connection)
    return result


def create_payment(travel_id, user_id):
    payment_id = get_payment_id(travel_id)
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        f'insert into Payments (travel_id, user_id, payment_id) values ("{travel_id}", {user_id}, {payment_id})')
    commit(connection)
    return payment_id


def get_list_payments(travel_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'select payment_id, title, date from Payments where travel_id="{travel_id}"')
    result = cursor.fetchall()
    commit(connection)
    return result


def is_well_amount(amount, travel_id, payment_id):
    amount = float(amount)
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f'select amount from Payments where travel_id="{travel_id}" and payment_id={payment_id}')
    all_amount = float(cursor.fetchone()[0])
    cursor.execute(f'select amount from PaymentsInfo where travel_id="{travel_id}" and payment_id={payment_id}')
    for item in cursor.fetchall():
        all_amount -= float(item[0])

    commit(connection)
    if all_amount - amount >= 0:
        return True
    return False


def my_debtors(travel_id, user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'select payment_id from Payments where travel_id="{travel_id}" and user_id={user_id}')
    payments = cursor.fetchall()
    result_t = {}
    for payment in payments:
        cursor.execute(
            f'select debtor_id, amount from PaymentsInfo where travel_id="{travel_id}" and payment_id={payment[0]} and status=0')
        users = cursor.fetchall()
        for user in users:
            if not (user[0] in result_t.keys()):
                result_t[int(user[0])] = float(user[1])
            else:
                result_t[user[0]] += float(user[1])
    result = {}
    for item in result_t.keys():
        username = db_dict.get_username_from_id(item)
        result[username] = result_t[item]
    commit(connection)

    return result


def i_debtors(travel_id, user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'select payment_id, user_id from Payments where travel_id="{travel_id}" and user_id!={user_id}')
    payments = cursor.fetchall()
    result_t = {}
    for payment in payments:
        cursor.execute(
            f'select amount from PaymentsInfo where travel_id="{travel_id}" and payment_id={payment[0]} and status=0 and debtor_id={user_id}')
        users = cursor.fetchall()
        for user in users:
            if not (payment[1] in result_t.keys()):
                result_t[int(payment[1])] = float(user[0])
            else:
                result_t[int(payment[1])] += float(user[0])
    result = {}
    for item in result_t.keys():
        username = db_dict.get_username_from_id(item)
        result[username] = result_t[item]
    commit(connection)

    return result


def update_param(travel_id, payment_id, param_name, param_value, is_string):
    connection = create_connection()
    cursor = connection.cursor()
    value = param_value
    cursor.execute(
        f'update Payments set {param_name}=(?) where travel_id="{travel_id}" and payment_id={payment_id}', (value,))
    commit(connection)


def get_payment_info(travel_id, payment_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        f'select title, date, amount, user_id from Payments where travel_id="{travel_id}" and payment_id={payment_id}')
    info = cursor.fetchone()
    commit(connection)
    return info


def remove_from_payment_info(travel_id, payment_id, debtor_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        f'delete from PaymentsInfo where travel_id="{travel_id}" and payment_id={payment_id} and debtor_id={debtor_id}')
    commit(connection)


def remove_payment(travel_id, payment_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        f'delete from Payments where travel_id="{travel_id}" and payment_id={payment_id}')
    cursor.execute(
        f'delete from PaymentsInfo where travel_id="{travel_id}" and payment_id={payment_id}')
    commit(connection)


def get_payment_info_id(travel_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(f'select payment_info_id from PaymentsInfo where travel_id="{travel_id}"')
    ids = cursor.fetchall()
    result = 1
    for id in ids:
        if result <= int(id[0]):
            result = int(id[0]) + 1
    commit(connection)
    return result


def get_user_payment_info(travel_id, payment_id, debtor_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        f'select amount, status, debtor_id from PaymentsInfo where travel_id="{travel_id}" and payment_id={payment_id} and debtor_id={debtor_id}')
    result = cursor.fetchone()
    commit(connection)
    return result


def get_users_in_payment(travel_id, payment_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        f'select debtor_id, amount from PaymentsInfo where travel_id="{travel_id}" and payment_id={payment_id}')
    users = cursor.fetchall()
    commit(connection)
    return users


# status:
# 0 - не закрыт долг
# 1 - закрыт
def create_payment_info(travel_id, payment_id, debtor_id, amount):
    payment_info_id = get_payment_info_id(travel_id)
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        f'insert into PaymentsInfo (travel_id, debtor_id, payment_info_id, status, amount, payment_id) values ("{travel_id}", {debtor_id}, {payment_info_id}, 0, {amount}, {payment_id})')
    commit(connection)
    return payment_info_id


def update_payment_info(travel_id, payment_id, debtor_id, parm_name, parm_value, is_string):
    connection = create_connection()
    cursor = connection.cursor()
    value = parm_value
    cursor.execute(
        f'update PaymentsInfo set {parm_name}=(?) where travel_id="{travel_id}" and payment_id={payment_id} and debtor_id={debtor_id}', (value,))
    commit(connection)
