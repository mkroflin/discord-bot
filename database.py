import constants
import pymysql

def get_log_by_date(start_date, end_date, cursor):
    sql = "SELECT id FROM log_table WHERE logDate > '%s' AND logDate < '%s'";
    cursor.execute(sql)
    return cursor.fetchall()

def get_name_id_by_name(table, var, value, cursor):
    sql = "SELECT id from {table} WHERE {var} = '{value}'".format(table=table, var=var, value=value)
    cursor.execute(sql)
    return cursor.fetchall()


def add_name(table_name, var, name, cursor):
    sql = "INSERT INTO %"

def connect():
    db = pymysql.connect(
        host=constants.DB_HOST,
        user=constants.DB_USERNAME,
        password=constants.DB_PASSWORD,
        database=constants.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

    return db

def create_table(cursor):
    sql = "CREATE TABLE `boss_name_table` (\
            `ID` int(11) PRIMARY KEY NOT NULL,\
            `bossName` varchar(30) NOT NULL\
            );"

    cursor.execute(sql)

if __name__ == '__main__':
    db = connect()
    cursor = db.cursor()
    #create_table(cursor)
    str = "mile"
    sql = "INSERT IGNORE INTO boss_name_table (bossName) VALUES ('{name}')".format(name=str)
    cursor.execute(sql)
    db.commit()
    sql = "SELECT * FROM boss_name_table"
    cursor.execute(sql)
    print(cursor.fetchall())