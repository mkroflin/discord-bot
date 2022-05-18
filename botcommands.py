import database as database
import re as re
import constants as constants
import logutils as logutils


def convert_input(args):
    input = {'boss' : args[0]}
    for i in range(1, len(args), 2):
        input[args[i]] = args[i + 1]

    return input

def upload_log(log_link, cursor):
    log_data = logutils.get_log_data(log_link)
    log_date, log_dur, success, boss_name_id = logutils.get_log_info(log_data, cursor)
    if float(log_dur) < constants.MIN_LOG_LENGTH or logutils.is_duplicate(log_data, cursor):
        return

    log_id = database.insert_log(log_link, log_date, log_dur, success, boss_name_id, cursor)

    phase_names, start_times, end_times, phase_durations = logutils.get_phase_info(log_data, success)
    last_phase_id = database.insert_phases(log_id, phase_names, start_times, end_times, phase_durations, cursor)

    database.insert_players(log_data, last_phase_id, phase_count, starts, ends, cursor)


def log_command(ctx, args):
    db = database.connect()
    cursor = db.cursor()
    for i in range(1, len(args), 1):
        upload_log(args[i], cursor)
        if i % 5 == 0:
            db.commit()
    db.close()