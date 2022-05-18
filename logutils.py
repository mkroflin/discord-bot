import database
import datetime
import constants
import json
import requests
import re

def is_duplicate(log_data, cursor):
    log_date = datetime.datetime.strptime(log_data['encounterStart'], '%Y-%m-%d %H:%M:%S %z')
    log_date = log_date.astimezone(datetime.timezone(datetime.timedelta()))
    t_range = datetime.timedelta(seconds=constants.DUPLICATE_DELTA)
    return len(database.get_log_by_date(log_date - t_range, log_date + t_range, cursor)) > 0

def get_log_data(link):
    request_http_full = requests.get(link)
    source = request_http_full.text
    var_ind = source.find("logData = ")
    start_ind = source.find("{", var_ind)
    end_ind = source.find(";", var_ind)
    return json.loads(source[start_ind:end_ind])

def get_log_info(log_data, cursor):
    tmp = list(map(int, re.sub('\D', ' ', log_data['encounterDuration']).split()))
    log_date = datetime.datetime.strptime(log_data['encounterStart'], '%Y-%m-%d %H:%M:%S %z')
    utc = datetime.timezone(datetime.timedelta())
    log_date = log_date.astimezone(utc)
    success = log_data['success']
    log_dur = "{:.3f}".format(tmp[0] * 60 + tmp[1] + tmp[2] / 1000)
    boss_name_id = database.get_name_id("boss_name", log_data['fightName'], cursor)
    return log_date, log_dur, success, boss_name_id


def get_phase_info(log_data, success):
    phase_names = []
    start_times = []
    end_times = []
    phase_durations = []

    for phase in log_data['phases']:
        if phase['breakbarPhase']:
            continue

        phase_name = phase['name']
        start = phase['start']
        end = 10000 if not success and phase == log_data['phases'][-1] else phase['end']

        print(phase_name, end - start)
        phase_names.append(phase_name)
        start_times.append(start)
        end_times.append(end)
        phase_durations.append(end - start)

    return phase_names, start_times, end_times, phase_durations


def get_player_dps_info(log_data, player_ind, start, end):
    tmp = log_data['graphData']['phases'][0]['players'][player_ind]['damage']['targets'][0]
    e = -1 if int(end) > 9999 else int(end) + 1
    s = int(start)
    player_name = log_data['players'][player_ind]['acc'].lower()
    class_name = log_data['players'][player_ind]['profession'].lower()
    start_dps = tmp[s] / (start + 0.00001)
    end_dps = tmp[e] / end
    phase_dps = (tmp[e] - tmp[s]) / (end - start)
    return player_name, class_name, start_dps, end_dps, phase_dps

def insert_log(log_data):
    tmp = list(map(int, re.sub('\D', ' ', log_data['encounterDuration']).split()))
    log_date = datetime.datetime.strptime(log_data['encounterStart'], '%Y-%m-%d %H:%M:%S %z')
    utc = datetime.timezone(datetime.timedelta())
    log_date = log_date.astimezone(utc)
    success = log_data['success']
    log_dur = "{:.3f}".format(tmp[0] * 60 + tmp[1] + tmp[2] / 1000)
    log_class = log_data['players'][0]['condi'] > 0
    boss_name = log_data['fightName'][:4]  # Delay's solution because Skorvald is bugged
    return log_date, log_dur, log_class, success, boss_name

if __name__ == '__main__':
    # log_data = get_log_data('https://dps.report/lz95-20220518-000311_void')
    log_data = get_log_data('https://dps.report/rFIL-20220428-223943_void')
    with open('test.json', 'w', encoding = 'utf-8') as f:
        f.write(json.dumps(log_data, separators=(',\n', ':')))

    log_date, log_time, success, boss_name = get_log_info(log_data)
    get_phase_info(log_data, success)
    phase_names, start_times, end_times, phase_durations = get_phase_info(log_data, success)
    print(phase_names, phase_durations)