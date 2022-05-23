import database
import datetime
import constants
import json
import requests
import re
import numpy
import math


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


def get_log_info(log_data):
    tmp = list(map(int, re.sub('\D', ' ', log_data['encounterDuration']).split()))
    log_date = datetime.datetime.strptime(log_data['encounterStart'], '%Y-%m-%d %H:%M:%S %z')
    utc = datetime.timezone(datetime.timedelta())
    log_date = log_date.astimezone(utc)
    success = log_data['success']
    log_dur = "{:.3f}".format(tmp[0] * 60 + tmp[1] + tmp[2] / 1000)
    boss_name_id = log_data['fightName']
    return log_date, log_dur, success, boss_name_id


def get_phase_info(log_data, success):
    phase_names = []
    start_times = []
    end_times = []
    phase_durations = []
    phase_inds = []

    for i, phase in zip(range(len(log_data['phases'])), log_data['phases']):
        if phase['breakbarPhase']:
            continue

        phase_name = phase['name']
        start = phase['start']
        end = 10000 if not success and phase == log_data['phases'][-1] else phase['end']
        phase_names.append(phase_name)
        start_times.append(start)
        end_times.append(end)
        phase_durations.append(end - start)
        phase_inds.append(i)

    return phase_names, start_times, end_times, phase_durations, phase_inds


def get_player_dps_info(log_data, phase_ind, player_ind, start, end):
    graph_data = log_data['graphData']['phases'][0]['players'][player_ind]['damage']['targets'][0]
    e = -1 if end > 9999 else int(end) + 1
    s = int(start)
    player_name = log_data['players'][player_ind]['acc'].lower()
    class_name = log_data['players'][player_ind]['profession'].lower()
    start_dps = graph_data[s] / (start + 0.000001)
    end_dps = graph_data[e] / end
    phase_damage = log_data['players'][player_ind]['details']['dmgDistributionsTargets'][phase_ind][0]['contributedDamage']
    phase_dur = -1 if e == -1 else log_data['phases'][phase_ind]['duration'] / 1000
    phase_dps = phase_damage / phase_dur
    return player_name, class_name, start_dps, end_dps, phase_dps


def get_player_info(log_data, start_times, end_times, phase_inds, last_phase_id):
    player_names = []
    class_names = []
    start_dpses = []
    end_dpses = []
    phase_dpses = []
    phase_ids = []
    for i, phase_id, start, end in zip(phase_inds, range(last_phase_id, last_phase_id + len(start_times)), start_times, end_times):
        for player_id in range(len(log_data['players'])):
            player_name, class_name, start_dps, end_dps, phase_dps = get_player_dps_info(log_data, i, player_id, start, end)
            player_names.append(player_name)
            class_names.append(class_name)
            start_dpses.append(start_dps)
            end_dpses.append(end_dps)
            phase_dpses.append(phase_dps)
            phase_ids.append(phase_id)

    return phase_ids, player_names, class_names, start_dpses, end_dpses, phase_dpses


def insert_log(log_data):
    tmp = list(map(int, re.sub('\D', ' ', log_data['encounterDuration']).split()))
    log_date = datetime.datetime.strptime(log_data['encounterStart'], '%Y-%m-%d %H:%M:%S %z')
    utc = datetime.timezone(datetime.timedelta())
    log_date = log_date.astimezone(utc)
    success = log_data['success']
    log_dur = "{:.3f}".format(tmp[0] * 60 + tmp[1] + tmp[2] / 1000)
    log_class = log_data['players'][0]['condi'] > 0
    boss_name = log_data['fightName']
    return log_date, log_dur, log_class, success, boss_name


if __name__ == '__main__':
    log_data = get_log_data('https://dps.report/7n3H-20220509-204715_matt')
    with open('test.json', 'w', encoding='utf-8') as f:
       f.write(json.dumps(log_data, separators=(',', ':')))

    tmp = log_data['graphData']['phases'][0]['players'][0]['damage']['targets'][0]

