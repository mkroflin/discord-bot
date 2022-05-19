import database
import constants
import logutils


def convert_input(args):
    input = dict()
    for i in range(0, len(args), 2):
        input[args[i]] = args[i + 1]

    return input

@database.timeit
def get_name_ids(type, names, cursor):
    unique_names = {x: database.get_name_id(type, x, cursor) for x in set(names)}
    return [unique_names[x] for x in names]

@database.timeit
def upload_log(log_link, cursor):
    log_data = logutils.get_log_data(log_link)
    log_date, log_dur, success, boss_name = logutils.get_log_info(log_data)
    if float(log_dur) < constants.MIN_LOG_LENGTH or logutils.is_duplicate(log_data, cursor):
        return

    boss_name_id = database.get_name_id("boss", boss_name, cursor)

    log_id = database.insert_log(log_link, log_date, log_dur, success, boss_name_id, cursor)

    phase_names, start_times, end_times, phase_durations = logutils.get_phase_info(log_data, success)

    phase_name_ids = [database.get_name_id("phase", x, cursor) for x in phase_names]
    last_phase_id = database.insert_phases(log_id, phase_name_ids, start_times, end_times, phase_durations, cursor)

    phase_ids, player_names, class_names, start_dpses, end_dpses, phase_dpses = logutils.get_player_info(log_data,
                                                                                                         start_times,
                                                                                                         end_times,
                                                                                                         last_phase_id)

    #TODO: optimize fetching name ids
    player_name_ids = get_name_ids("player", player_names, cursor)
    class_name_ids = get_name_ids("class", class_names, cursor)

    database.insert_players(phase_ids, player_name_ids, class_name_ids, start_dpses, end_dpses, phase_dpses, cursor)


@database.timeit
def get_duration_with_params(params, flags, cursor):
    boss_name_id, boss_name = database.get_exact_name_id("boss", params["-b"], cursor)

    phase_name_id = database.get_exact_name_id("phase", "Full Fight", cursor)
    phase_name = ""
    success = False
    if "-p" in flags:
        phase_name_id, phase_name = database.get_exact_name_id("phase", params["-p"], cursor)
        success = 0

    player_name_id = -1
    player_name = ""
    if "-pl" in flags:
        player_name_id, player_name = database.get_exact_name_id("player", params["-p"], cursor)

    class_name_id = -1
    class_name = ""
    if "-pl" in flags:
        class_name_id, class_name = database.get_exact_name_id("player", params["-p"], cursor)

    logs = database.get_data_for_duration(boss_name_id, success, phase_name_id, player_name_id, class_name_id, cursor)
    query = " ".join([boss_name, phase_name, player_name, class_name])
    result = "\n".join(["{log} Phase duration: {pd}".format(log=r["link"], pd=r["phase_duration"], query=query) for r in logs])
    return query, result


def log_command(ctx, args):
    db = database.connect()
    cursor = db.cursor()
    for i in range(1, len(args), 1):
        upload_log(args[i], cursor)
        print("Uploaded log: {}".format(args[i]))
        if i % 5 == 0:
            db.commit()
    db.close()


def dur_command(ctx, args):
    for i in range(0, len(args), 2):
        if "-" not in args[i]:
            ctx.send("Input parameters were wrong. Check that you have a flag followed by value.")
            return

    params = convert_input(args)
    flags = params.keys()
    if "-b" not in flags:
        ctx.send("Boss parameter was not given.")
        return

    db = database.connect()
    cursor = db.cursor()
    print(params)
    return get_duration_with_params(params, flags, cursor)


if __name__ == '__main__':
    # log_link = 'https://dps.report/d5cQ-20220517-193416_vg'
    db = database.connect()
    params = convert_input(["-b""Matthias"])
    #get_duration_with_params()
    db.close()
