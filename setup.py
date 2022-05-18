import database as database

if __name__ == '__main__':
    db = database.connect()
    cursor = db.cursor()
    database.create_tables(cursor)
    db.commit()