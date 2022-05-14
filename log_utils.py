import database
import datetime
import constants


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


def is_duplicate(log_data, cursor):
    log_date = datetime.datetime.strptime(log_data['encounterStart'], '%Y-%m-%d %H:%M:%S %z')
    log_date = log_date.astimezone(datetime.timezone(datetime.timedelta()))
    t_range = datetime.timedelta(seconds=constants.DUPLICATE_DELTA)
    return len(database.get_log_by_date(log_date - t_range, log_date + t_range, cursor)) > 0

def get_name_id(table_name, var, name, cursor):
    name_ids = database.get_name_id_by_name(table_name, var, name, cursor)
    if len(name_ids) == 0:
        name_ids = database.add_name(table_name, var, name, cursor)

    return name_ids[0]['id']