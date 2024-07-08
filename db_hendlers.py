def get_user(cursor, user_id):
    return cursor.execute("SELECT * FROM users WHERE user_id=?;", (user_id, )).fetchone()


def add_user(conn, cursor, user_id, city, ref_code):
    try:
        cursor.execute("INSERT INTO users (user_id, city, who_ref) VALUES (?, ?, ?);", (user_id, city, ref_code, ))
        conn.commit()
        return True
    except:
        return False


def get_worker(cursor, user_id):
    return cursor.execute("SELECT * FROM users WHERE user_id=? AND status=?;", (user_id, 1, )).fetchone()


def get_form(cursor, model_id):
    return cursor.execute("SELECT * FROM forms WHERE model_id=?;", (model_id, )).fetchone()


def delete_form(conn, cursor, model_id):
    try:
        cursor.execute("DELETE FROM forms WHERE model_id=?;", (model_id, ))
        conn.commit()
        return True
    except:
        return False


def change_status(conn, cursor, user_id):
    try:
        cursor.execute("UPDATE users SET status=? WHERE user_id=?;", (1, user_id, ))
        conn.commit()
        cursor.execute("INSERT INTO workers (worker_id) VALUES (?);", (user_id, ))
        conn.commit()
        return True
    except:
        return False


def add_girl(conn, cursor, worker_id, data):
    try:
        cursor.execute("INSERT INTO forms (girl_name, age, price_hour, about, services, photos, nude_photos, worker_id) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?);", (data[0], data[1], data[2], data[3], data[4], data[5], data[6], worker_id,))
        conn.commit()
        return True
    except Exception as ex:
        print(ex)
        return False



def get_all_girls(cursor):
    return cursor.execute("SELECT * FROM forms;").fetchall()


def get_all_girls_worker(cursor, user_id):
    return cursor.execute("SELECT * FROM forms WHERE worker_id=?;", (user_id, )).fetchall()


def get_worker_stat(cursor, worker_id):
    return cursor.execute("SELECT * FROM workers WHERE worker_id=?;", (worker_id, )).fetchone()


def get_count_girls(cursor):
    return cursor.execute("SELECT COUNT(*) FROM forms;").fetchone()[0]