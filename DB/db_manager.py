import os
import sqlite3

is_test = False


def set_test():
    global is_test
    if os.path.exists('test.db') and not is_test:
        os.remove('test.db')
    is_test = True


def create_connection():
    global is_test
    if not is_test:
        return sqlite3.connect('DB\\db.db')
    else:
        return sqlite3.connect('test.db')


def commit(connection):
    connection.commit()
    connection.close()


def create_database():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS UsersDict (
	    user_id INTEGER,
	    username TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER,
	        age INTEGER,
	        country TEXT,
	        city TEXT,
	        bio TEXT,
	        payload TEXT
	        );
    ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS UsersFullInfo (
                                user_id INTEGER,
                    	        gender INTEGER,
                    	        interests TEXT
                    	        );
                        ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Places (
                user_id INTEGER,
    	        country_id INTEGER,
    	        city_id INTEGER
    	        );
        ''')

    cursor.execute('''
                CREATE TABLE IF NOT EXISTS Traveles (
                    user_id INTEGER,
        	        title TEXT,
        	        description TEXT,
        	        travel_id TEXT
        	        );
            ''')
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Locations (
                        travel_id TEXT,
            	        location_name TEXT,
            	        place_id INTEGER,
            	        start_date TEXT,
            	        end_date TEXT,
            	        location_id INTEGER
            	        );
                ''')
    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS FriendsInTravel (
                            travel_id TEXT,
                	        user_id INTEGER
                	        );
                    ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Notes (
                travel_id TEXT,
    	        is_public TEXT,
    	        title TEXT,
    	        description TEXT,
    	        note_id INTEGER
    	        );
        ''')
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS NotesInfo (
                    travel_id TEXT,
        	        note_id INTEGER,
        	        url TEXT
        	        );
            ''')
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS PlacesInfo (
                        place_id INTEGER,
            	        lat TEXT,
            	        long TEXT
            	        );
                ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SearchExchange (
                            travel_id TEXT,
                	        username TEXT,
                	        age INTEGER
                	        );
                    ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Payments (
                                travel_id TEXT,
                    	        payment_id INTEGER,
                    	        date TEXT,
                    	        amount FLOAT,
                    	        user_id INTEGER,
                    	        title TEXT
                    	        );
                        ''')
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS PaymentsInfo (
                                    travel_id TEXT,
                        	        debtor_id INTEGER,
                                    status INTEGER,
                                    payment_info_id INTEGER,
                                    payment_id INTEGER,
                                    amount FLOAT
                        	        );
                            ''')
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS GuideInfo (
                                        user_id INTEGER,
                                        guide_name TEXT
                            	        );
                                ''')
    commit(connection)
