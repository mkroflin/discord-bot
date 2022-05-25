import constants
import pymysql
import time
import os


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("{function_name}: {duration:.2f} s".format(function_name=func.__name__, duration=end - start))
        return result

    return wrapper


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


def get_exact_name_id(type, name, cursor):
    sql = "SELECT ID, name, short_name FROM names WHERE type = '{type}'".format(type=type)
    cursor.execute(sql)
    result = sorted(
        [(weighted_distance(name, x['short_name']), x['ID'], x['name'], x['short_name']) for x in cursor.fetchall()])
    return result[0][1:3]


@timeit
def get_log_by_date(start_date, end_date, cursor):
    sql = "SELECT id FROM log WHERE log.date > '{start}' AND log.date < '{end}'".format(start=start_date, end=end_date)
    cursor.execute(sql)
    return cursor.fetchall()


def get_name_id_by_name(type, value, cursor):
    sql = "SELECT id from names WHERE short_name = '{value}' AND type = '{type}'".format(value=value, type=type)
    cursor.execute(sql)
    return cursor.fetchall()


def add_name(type, name, short_name, cursor):
    sql = "INSERT INTO names (name, short_name, type) " \
          "VALUES ('{name}', '{short_name}', '{type}')".format(name=name,
                                                               short_name=short_name,
                                                               type=type)
    cursor.execute(sql)
    return cursor.lastrowid


def get_names_by_name(type, name, cursor):
    sql = "SELECT name, short_name FROM names WHERE type = '{}' ".format(type)
    if name != "ALL":
        sql += "AND name = '{}' ".format(name)

    sql += "LIMIT {}".format(constants.QUERY_LIMIT)
    print(sql)
    cursor.execute(sql)
    return cursor.fetchall()


def get_names_by_short_name(type, short_name, cursor):
    sql = "SELECT name, short_name FROM names WHERE type = '{}' " \
          "AND short_name = '{}'".format(type, short_name)

    cursor.execute(sql)
    return cursor.fetchall()


def update_name(type, name, short_name, cursor):
    short_names = get_names_by_short_name(type, short_name, cursor)
    if len(short_names) != 0:
        return short_names[0]["name"]

    names = get_names_by_name(type, name, cursor)
    if not names:
        add_name(type, name, short_name, cursor)
    else:
        sql = "UPDATE names SET short_name = '{short_name}' " \
              "WHERE type = '{type}' AND name = '{name}'".format(name=name,
                                                                 short_name=short_name,
                                                                 type=type)
        cursor.execute(sql)

    return short_name


def get_name_id(table, name, cursor):
    name_ids = get_name_id_by_name(table, name, cursor)
    if len(name_ids) == 0:
        return add_name(table, name, name, cursor)

    return name_ids[0]['id']


def get_name_by_id(id, cursor):
    sql = "SELECT short_name FROM names WHERE ID = {}".format(id)
    cursor.execute(sql)
    return cursor.fetchall()[0]["short_name"]


@timeit
def insert_log(log_link, log_date, log_dur, success, boss_name_id, cursor):
    sql = "INSERT INTO log (link, date, duration, success, boss_name_id) " \
          "VALUES ('{link}', '{date}', {duration}, {success}, {boss_name_id}" \
          ");".format(link=log_link, date=log_date, duration=log_dur, success=success, boss_name_id=boss_name_id)

    cursor.execute(sql)
    return cursor.lastrowid


@timeit
def insert_phases(log_id, phase_name_ids, start_times, end_times, phase_durations, cursor):
    sql = "INSERT INTO phase (log_id, phase_name_id, start_time, end_time, phase_duration) VALUES "
    values = ["({}, {}, {}, {}, {})".format(log_id, a, b, c, d) for a, b, c, d in
              zip(phase_name_ids, start_times, end_times, phase_durations)]

    sql += ",\n".join(values) + ";"
    cursor.execute(sql)
    return cursor.lastrowid


@timeit
def insert_players(phase_ids, player_name_ids, class_name_ids, start_dpses, end_dpses, phase_dpses, cursor):
    sql = "INSERT INTO dps (phase_id, player_name_id, class_name_id, start_dps, end_dps, phase_dps) VALUES "
    values = values = ["({}, {}, {}, {}, {}, {})".format(a, b, c, d, e, f) for a, b, c, d, e, f in
                       zip(phase_ids, player_name_ids, class_name_ids, start_dpses, end_dpses, phase_dpses)]

    sql += ",\n".join(values) + ";"
    cursor.execute(sql)
    return cursor.lastrowid


@timeit
def get_data_for_duration(boss_name_id, success, phase_name_id, player_name_id, class_name_id, dur_type, cursor):
    sql_table = "SELECT DISTINCT log.link, phase.phase_duration FROM log\n" \
                "INNER JOIN phase ON phase.log_id = log.ID\n" \
                "INNER JOIN dps ON dps.phase_id = phase.ID\n"

    sql_condition = "WHERE log.boss_name_id = {} ".format(boss_name_id)
    if success:
        sql_condition += "AND log.success = TRUE\n"

    if phase_name_id != -1:
        sql_condition += "AND phase.phase_name_id = {}\n".format(phase_name_id)

    if player_name_id != -1:
        sql_condition += "AND dps.player_name_id = {}\n".format(player_name_id)

    if class_name_id != -1:
        sql_condition += "AND dps.class_name_id = {}\n".format(class_name_id)

    sql_condition += "ORDER BY phase.{} ASC\n".format(dur_type)
    sql_condition += "LIMIT {} ".format(constants.QUERY_LIMIT)
    cursor.execute(sql_table + sql_condition)
    return cursor.fetchall()


@timeit
def get_data_for_dps(boss_name_id, success, phase_name_id, player_name_id, class_name_id, dps_type, cursor):
    sql_table = "SELECT DISTINCT log.link, dps.{}, dps.player_name_id, dps.class_name_id FROM log\n" \
                "INNER JOIN phase ON phase.log_id = log.ID\n" \
                "INNER JOIN dps ON dps.phase_id = phase.ID\n".format(dps_type)

    sql_condition = "WHERE log.boss_name_id = {} ".format(boss_name_id)
    if success:
        sql_condition += "AND log.success = TRUE\n"

    if phase_name_id != -1:
        sql_condition += "AND phase.phase_name_id = {}\n".format(phase_name_id)

    if player_name_id != -1:
        sql_condition += "AND dps.player_name_id = {}\n".format(player_name_id)

    if class_name_id != -1:
        sql_condition += "AND dps.class_name_id = {}\n".format(class_name_id)

    sql_condition += "ORDER BY dps.{} DESC ".format(dps_type)
    sql_condition += "LIMIT {} ".format(constants.QUERY_LIMIT)
    cursor.execute(sql_table + sql_condition)
    return cursor.fetchall()


def connect(config):
    return pymysql.connect(
        host=config["DB_HOST"],
        user=config["DB_USERNAME"],
        password=config["DB_PASSWORD"],
        database=config["DB_NAME"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )


def create_tables(cursor):
    cursor.execute(get_create_log_sql())
    cursor.execute(get_create_names_sql())
    cursor.execute(get_create_phase_sql())
    cursor.execute(get_create_dps_sql())


def drop_tables(cursor):
    cursor.execute(get_drop_all_sql())


def get_create_names_sql():
    return "CREATE TABLE IF NOT EXISTS `names` (" \
           "`ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT," \
           "`name` varchar(30) NOT NULL," \
           "`short_name` varchar(30) NOT NULL," \
           "`type` varchar(30) NOT NULL," \
           "UNIQUE(`short_name`, `type`)" \
           ");"


def get_create_dps_sql():
    return "CREATE TABLE IF NOT EXISTS`dps` (" \
           "`ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT," \
           "`phase_id` int(11) NOT NULL," \
           "`player_name_id` int(11) NOT NULL," \
           "`class_name_id` int(11) NOT NULL," \
           "`start_dps` int(11) NOT NULL," \
           "`end_dps` int(11) NOT NULL," \
           "`phase_dps` int(11) NOT NULL," \
           "FOREIGN KEY (`phase_id`) REFERENCES `phase`(`ID`)" \
           ");"


def get_create_phase_sql():
    return "CREATE TABLE IF NOT EXISTS `phase` (" \
           "`ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT," \
           "`log_id` int(11) NOT NULL," \
           "`phase_name_id` int(11) NOT NULL," \
           "`start_time` float NOT NULL," \
           "`end_time` float NOT NULL," \
           "`phase_duration` float NOT NULL" \
           ");"


def get_create_log_sql():
    return "CREATE TABLE IF NOT EXISTS `log` (" \
           "`ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT," \
           "`link` varchar(50) NOT NULL," \
           "`date` datetime NOT NULL," \
           "`duration` float NOT NULL," \
           "`success` tinyint(1) NOT NULL," \
           "`boss_name_id` int(11) NOT NULL" \
           ");"


def get_drop_all_sql():
    return "DROP TABLE IF EXISTS names;" \
           "DROP TABLE IF EXISTS class_name;" \
           "DROP TABLE IF EXISTS dps;" \
           "DROP TABLE IF EXISTS log;" \
           "DROP TABLE IF EXISTS phase;"
