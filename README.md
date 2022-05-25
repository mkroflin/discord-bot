# Log bot for Guild Wars 2 encounters
## Features
1. Search encounter logs by phase duration, phase start/end
2. Search encounter logs by class dps
    1. Total phase DPS
    2. DPS at start/end of phase

## Commands
To list all commands use `$help`. Template for a command is
```
$command -b [boss] -p [phase] -t [type] -c [class] -pl [player]
```
where each template has different mandatory/optional arguments depending on the command itself. Bellow you can see for each command-type (```dps```, ```dur```, ```boon̨̨```)
1. ```dps -b skor -p "Phase 3" -t full -c ren -pl Tantor``` will give skorvald logs sorted by phase 3 dps for renegade played by Tantor
2. ```dur -b skor -p "Phase 2" -t start``` will give skorvald logs sorted by start of Phase 2

All arguments except ```type``` will be partially matched. This is because ```type``` is a specific flag that indicates which segment you want to inspect relative to the phase.
Available types are ```full```, ```start``` and ```end```. Each command-type has it's own required arguments and optional arguments. Optional arguments are only additional output
filters and parameters. 

## Setup and run the bot
First install requirements by using `$ pip install -r requirements.txt` and then create an `.env` file where your DB and Discord token info will be stored. File should contain 
the following variables
```
DB_HOST = my_db_ip
DB_USERNAME = my_db_username
DB_PASSWORD = my_db_password
DB_NAME = my_db_name

DISCORD_TOKEN = my_token_name
my_token_name = my_discord_token
```
The recursive token naming allow you to have multiple tokens stored and by renaming the variable `DISCORD_TOKEN` you can switch between them. 
After this is done, you can run the bot by running the main script `python main.py`.
## TODO
- Configurable tables
- Add queries on boons
- Run the bot on a remote server
  - Add docker files
  - Deploy CI/CD with Github and a (free) Cloud service
- Code optimizations
  - Optimize deconstruction of data
  - Optimize DB calls