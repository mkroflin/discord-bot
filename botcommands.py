import dotenv

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
        print("Log is duplicate or too short")
        return

    boss_name_id = database.get_name_id("boss", boss_name, cursor)

    log_id = database.insert_log(log_link, log_date, log_dur, success, boss_name_id, cursor)

    phase_names, start_times, end_times, phase_durations, phase_inds = logutils.get_phase_info(log_data, success)

    phase_name_ids = [database.get_name_id("phase", x, cursor) for x in phase_names]
    last_phase_id = database.insert_phases(log_id, phase_name_ids, start_times, end_times, phase_durations, cursor)

    phase_ids, player_names, class_names, start_dpses, end_dpses, phase_dpses = logutils.get_player_info(log_data,
                                                                                                         start_times,
                                                                                                         end_times,
                                                                                                         phase_inds,
                                                                                                         last_phase_id
                                                                                                         )

    # TODO: optimize fetching name ids
    player_name_ids = get_name_ids("player", player_names, cursor)
    class_name_ids = get_name_ids("class", class_names, cursor)

    database.insert_players(phase_ids, player_name_ids, class_name_ids, start_dpses, end_dpses, phase_dpses, cursor)


@database.timeit
def get_duration_with_params(params, flags, cursor):
    dur_types = {
        "start": "start_time",
        "end": "end_time",
        "full": "phase_duration"
    }

    boss_name_id, boss_name = database.get_exact_name_id("boss", params["-b"], cursor)

    phase_name_id = database.get_exact_name_id("phase", "Full Fight", cursor)
    phase_name = ""
    success = True
    if "-p" in flags:
        phase_name_id, phase_name = database.get_exact_name_id("phase", params["-p"], cursor)
        success = False

    player_name_id = -1
    player_name = ""
    if "-pl" in flags:
        player_name_id, player_name = database.get_exact_name_id("player", params["-pl"], cursor)

    class_name_id = -1
    class_name = ""
    if "-c" in flags:
        class_name_id, class_name = database.get_exact_name_id("class", params["-c"], cursor)

    dur_type = "phase_duration"
    if "-t" in flags and params["-t"] in dur_types.keys():
        dur_type = dur_types[params["-t"]]

    logs = database.get_data_for_duration(boss_name_id, success, phase_name_id, player_name_id, class_name_id, dur_type,
                                          cursor)
    query = " ".join([boss_name, dur_type, " of ", phase_name, player_name, class_name])
    result = "\n".join(["{log} Time: {pd}".format(log=r["link"], pd=r[dur_type]) for r in logs])
    return query, result


@database.timeit
def get_dps_with_params(params, flags, cursor):
    dps_types = {
        "start": "start_dps",
        "end": "end_dps",
        "phase": "phase_dps"
    }

    boss_name_id, boss_name = database.get_exact_name_id("boss", params["-b"], cursor)

    phase_name_id = database.get_exact_name_id("phase", "Full Fight", cursor)
    phase_name = ""
    success = True
    if "-p" in flags:
        phase_name_id, phase_name = database.get_exact_name_id("phase", params["-p"], cursor)
        success = False

    player_name_id = -1
    player_name = ""
    if "-pl" in flags:
        player_name_id, player_name = database.get_exact_name_id("player", params["-pl"], cursor)

    class_name_id = -1
    class_name = ""
    if "-c" in flags:
        class_name_id, class_name = database.get_exact_name_id("class", params["-c"], cursor)

    dps_type = "phase_dps"
    if "-t" in flags and params["-t"] in dps_types.keys():
        dps_type = dps_types[params["-t"]]

    logs = database.get_data_for_dps(boss_name_id, success, phase_name_id, player_name_id, class_name_id, dps_type,
                                     cursor)

    query = " ".join([boss_name, dps_type, "of", phase_name, player_name, class_name])
    result = "\n".join(["{log} {player} {class_name} DPS: {dps}".format(log=r["link"],
                                                                        dps=r[dps_type],
                                                                        player=database.get_name_by_id(
                                                                            r["player_name_id"], cursor),
                                                                        class_name=database.get_name_by_id(
                                                                            r["class_name_id"], cursor)) for r in logs])

    return query, result


def log_command(args, db):
    cursor = db.cursor()
    for i in range(1, len(args), 1):
        upload_log(args[i], cursor)
        print("Uploaded log: {}".format(args[i]))
        if i % 5 == 0:
            db.commit()


def is_valid_args(args):
    for i in range(0, len(args), 2):
        if "-" not in args[i]:
            return False

    return True


def dur_command(ctx, args, db):
    if not is_valid_args(args):
        return "", "Input parameters were wrong. Check that you have a flag followed by value."

    params = convert_input(args)
    flags = params.keys()
    if "-b" not in flags:
        return "", "Boss parameter was not given."

    cursor = db.cursor()
    return get_duration_with_params(params, flags, cursor)


def dps_command(ctx, args, db):
    if not is_valid_args(args):
        return "", "Input parameters were wrong. Check that you have a flag followed by value."

    params = convert_input(args)
    flags = params.keys()
    if "-b" not in flags:
        return "", "Boss parameter was not given."

    cursor = db.cursor()
    return get_dps_with_params(params, flags, cursor)


def flag_command():
    return "List of all flags:\n" \
           "-t point of the phase, 'start' (start of phase), " \
           "'end' (end of phase), 'full' [default] for specific phase\n" \
           "-b boss_name, mandatory for dps and dur commands\n" \
           "-pl player_name\n" \
           "-p phase_name (full_name), 'Full Fight' [default]\n" \
           "-c class_name"


def alias_command(args, db):
    name_types = {
        "-b": "boss",
        "-pl": "player",
        "-c": "class"
    }
    if len(args) == 0 or args[0] not in name_types.keys():
        return "You have to specify one of the following flags as first argument:\n{}".format(list(name_types.keys()))

    if len(args) > 3:
        return "You gave too many arguments. Make sure to use quotation marks when name contains more than 1 word"

    cursor = db.cursor()

    if len(args) == 3:
        if args[2] == 'ALL':
            return "'ALL' is a keyword. Please choose a different alias"
        updated_name = database.update_name(name_types[args[0]], args[1], args[2], cursor)
        if updated_name == args[2]:
            db.commit()
            return "Successfully changed alias for {} to {}".format(args[1], args[2])

        return "Alias {} already exists for {}. Please choose a different alias".format(args[2], updated_name)

    name = "ALL"
    if len(args) == 2:
        name = args[1]

    all_names = database.get_names_by_name(name_types[args[0]], name, cursor)
    return "List of alias for {}:\n{}".format(name, "\n".join(["Name: {} Alias: {}".format(x["name"],
                                                                                           x["short_name"]) for x in
                                                               all_names]))
