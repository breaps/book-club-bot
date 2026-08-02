import sqlite3

DB = "club.db"


def connect():
    return sqlite3.connect(DB)


def init_db():
    db = connect()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author INTEGER,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS current(
        title TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress(
        user_id INTEGER,
        percent INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history(
        title TEXT
    )
    """)

    db.commit()
    db.close()



def add_user(uid,name):
    db=connect()
    cur=db.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users VALUES (?,?)",
        (uid,name)
    )

    db.commit()
    db.close()



def users():
    db=connect()
    cur=db.cursor()

    cur.execute(
        "SELECT id FROM users"
    )

    result=[x[0] for x in cur.fetchall()]

    db.close()

    return result



def add_book(title,uid):

    db=connect()
    cur=db.cursor()

    cur.execute(
        """
        INSERT INTO books(title,author,status)
        VALUES(?,?,?)
        """,
        (title,uid,"candidate")
    )

    db.commit()
    db.close()



def candidates():

    db=connect()
    cur=db.cursor()

    cur.execute(
        """
        SELECT title FROM books
        WHERE status='candidate'
        """
    )

    result=[x[0] for x in cur.fetchall()]

    db.close()

    return result



def set_current(title):

    db=connect()
    cur=db.cursor()

    cur.execute(
        "DELETE FROM current"
    )

    cur.execute(
        "INSERT INTO current VALUES(?)",
        (title,)
    )

    cur.execute(
        """
        UPDATE books
        SET status='chosen'
        WHERE title=?
        """,
        (title,)
    )

    db.commit()
    db.close()



def get_current():

    db=connect()
    cur=db.cursor()

    cur.execute(
        "SELECT title FROM current"
    )

    result=cur.fetchone()

    db.close()

    return result[0] if result else None



def add_progress(uid,percent):

    db=connect()
    cur=db.cursor()

    cur.execute(
        "DELETE FROM progress WHERE user_id=?",
        (uid,)
    )

    cur.execute(
        "INSERT INTO progress VALUES(?,?)",
        (uid,percent)
    )

    db.commit()
    db.close()



def get_progress():

    db=connect()
    cur=db.cursor()

    cur.execute(
        """
        SELECT users.name,progress.percent
        FROM progress
        JOIN users
        ON users.id=progress.user_id
        """
    )

    result=cur.fetchall()

    db.close()

    return result



def finish_book():

    book=get_current()

    if not book:
        return None

    db=connect()
    cur=db.cursor()

    cur.execute(
        "INSERT INTO history VALUES(?)",
        (book,)
    )

    cur.execute(
        "DELETE FROM current"
    )

    cur.execute(
        "DELETE FROM progress"
    )

    db.commit()
    db.close()

    return book



def history():

    db=connect()
    cur=db.cursor()

    cur.execute(
        """
        SELECT title
        FROM history
        ORDER BY rowid DESC
        LIMIT 5
        """
    )

    result=[x[0] for x in cur.fetchall()]

    db.close()

    return result
