import discordbot
import dotenv
import constants


def import_and_validate_env_variables():
    config = dotenv.dotenv_values("../resources/.env")
    for key in constants.REQUIRED_ENV_VARIABLES:
        if key not in config.keys():
            print("Missing {} in .env file. Please add it".format(key))
            exit(1)

    config["DISCORD_TOKEN"] = config[config["DISCORD_TOKEN"]]

    return config


if __name__ == '__main__':
    bot = discordbot.LogBot(import_and_validate_env_variables())
    bot.run()
