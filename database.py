import constants
import pymysql

def weighted_distance(s1, s2):
    s1 = s1.lower()
    s2 = s2.upper()
    m = len(s1)
    n = len(s2)
    cost_delete = 100
    cost_substitute = 50
    d = [[cost_delete * i] for i in range(1, m + 1)]
    d.insert(0, [0] + list(range(20, n + 20)))
    for j in range(n):
        for i in range(m):
            cost_insert = m - i
            if s1[i].lower() == s2[j].lower():
                cost = 0
            else:
                cost = cost_substitute
            d[i + 1].insert(j + 1, min(d[i][j + 1] + cost_delete,
                                       d[i + 1][j] + cost_insert,
                                       d[i][j] + cost))
    return d[-1][-1]

def get_exact_name_id(table, name, cursor):
    sql = "SELECT ID, short_name FROM {table}".format(table=table)
    cursor.execute(sql)
    return sorted([(weighted_distance(name, x['short_name']), x['ID']) for x in cursor.fetchall()])[0][1]

def get_log_by_date(start_date, end_date, cursor):
    sql = "SELECT id FROM log_table WHERE logDate > '%s' AND logDate < '%s'"
    cursor.execute(sql)
    return cursor.fetchall()

def get_name_id_by_name(table, value, cursor):
    sql = "SELECT id from {table} WHERE short_name = '{value}'".format(table=table, value=value)
    cursor.execute(sql)
    return cursor.fetchall()

def add_name(table, value, cursor):
    sql = "INSERT INTO {table} (name, short_name) VALUES ('{value}', '{value}')".format(table=table, var=var, value=value)
    cursor.execute(sql)
    return cursor.lastrowid

def get_name_id(table, name, cursor):
    name_ids = get_name_id_by_name(table, name, cursor)
    if len(name_ids) == 0:
        return add_name(table, name, cursor)

    return name_ids[0]['id']

def insert_log(log_link, log_date, log_dur, success, boss_name_id, cursor):
    sql = "INSERT INTO log (link, date, duration, success, boss_name_id) \
           VALUES ('{link}, {date}, {duration}, {success}, {boss_name_id} \
           )".format(link=log_link, date=log_date, duration=log_dur, success=success, boss_name_id=boss_name_id)

    cursor.execute(sql)
    return cursor.lastrowid

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

def create_tables(cursor):
    cursor.execute(get_create_log_sql())
    cursor.execute(get_create_boss_name_sql())
    cursor.execute(get_create_class_name_sql())
    cursor.execute(get_create_phase_name_sql())
    cursor.execute(get_create_player_name_sql())
    cursor.execute(get_create_phase_sql())
    cursor.execute(get_create_dps_sql())


def get_create_boss_name_sql():
    return "CREATE TABLE IF NOT EXISTS `boss_name` (\
            `ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,\
            `name` varchar(30) NOT NULL UNIQUE,\
            `short_name` varchar(30) NOT NULL UNIQUE\
            );"


def get_create_player_name_sql():
    return "CREATE TABLE IF NOT EXISTS `player_name` (\
            `ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,\
            `name` varchar(30) NOT NULL UNIQUE,\
            `short_name` varchar(30) NOT NULL\
            );"


def get_create_phase_name_sql():
    return "CREATE TABLE IF NOT EXISTS `phase_name` (\
            `ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,\
            `name` varchar(30) NOT NULL UNIQUE,\
            `short_name` varchar(30) NOT NULL\
            );"


def get_create_class_name_sql():
    return "CREATE TABLE IF NOT EXISTS `class_name` (\
            `ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,\
            `name` varchar(30) NOT NULL UNIQUE,\
            `short_name` varchar(30) NOT NULL\
            );"

def get_create_dps_sql():
    return "CREATE TABLE IF NOT EXISTS`dps` (\
            `ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,\
            `phase_id` int(11) NOT NULL,\
            `player_name_id` int(11) NOT NULL,\
            `class_name_id` int(11) NOT NULL,\
            `start_dps` int(11) NOT NULL,\
            `end_dps` int(11) NOT NULL,\
            `phase_dps` int(11) NOT NULL,\
            FOREIGN KEY (`player_name_id`) REFERENCES `player_name`(`ID`),\
            FOREIGN KEY (`class_name_id`) REFERENCES `class_name`(`ID`),\
            FOREIGN KEY (`phase_name_id`) REFERENCES `phase`(`ID`)\
            );"


def get_create_phase_sql():
    return "CREATE TABLE IF NOT EXISTS `phase` (\
            `ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,\
            `log_id` int(11) NOT NULL,\
            `phase_name_id` int(11) NOT NULL,\
            `start_time` float NOT NULL,\
            `end_time` float NOT NULL,\
            `phase_duration` float NOT NULL,\
            FOREIGN KEY (`phase_name_id`) REFERENCES `phase_name`(`ID`)\
            );"


def get_create_log_sql():
    return "CREATE TABLE IF NOT EXISTS `log` (\
            `ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,\
            `link` varchar(50) NOT NULL,\
            `date` datetime NOT NULL,\
            `duration` float NOT NULL,\
            `success` tinyint(1) NOT NULL,\
            `boss_name_id` int(11) NOT NULL,\
            FOREIGN KEY (`boss_name_id`) REFERENCES `boss_name`(`ID`)\
            );"


if __name__ == '__main__':
    db = connect()
    cursor = db.cursor()
    create_tables(cursor)
    db.commit()