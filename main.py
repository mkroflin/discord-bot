import discordbot
import dotenv
import constants


def import_and_validate_env_variables():
    config = dotenv.dotenv_values(".env")
    for key in constants.REQUIRED_ENV_VARIABLES:
        if key not in config.keys():
            print("Missing {} in .env file. Please add it")
            exit(1)

    return config


if __name__ == '__main__':
    bot = discordbot.LogBot(import_and_validate_env_variables())
    bot.run()
