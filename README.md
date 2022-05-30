# Log bot for Guild Wars 2 encounters
## Features
1. Search encounter logs by phase duration, phase start/end
2. Search encounter logs by class dps
    1. Total phase DPS
    2. DPS at start/end of phase

## Commands
### Inserting logs
To insert logs use the command `$log` and then a list of logs separated whitespace.
### Queries 
Current commands in use are `$dps` and `$dur` both of which are used with the following form
```
$command -b [boss] -p [phase] -t [type] -c [class] -pl [player] -d [date]
```
where each template has different mandatory/optional arguments depending on the command itself. Bellow you can see for each command-type (```dps```, ```dur```, ```boon̨̨```)
1. ```dps -b skor -p "Phase 3" -t full -c ren -pl Tantor``` will give skorvald logs sorted by phase 3 dps for renegade played by Tantor
2. ```dur -b skor -p "Phase 2" -t start``` will give skorvald logs sorted by start of Phase 2

If names contain more than one word, they have to be given in quotation marks for example `"Vale Guardian"`. All arguments except ```type``` will be partially matched. This is because ```type``` is a specific flag that indicates which segment you want to inspect relative to the phase.
Available types are ```full```, ```start``` and ```end```. For the date flag, you can either give a date (ISO format) or 
an expression of the form `[num][short]`. Number expressed the amount of shorts you want and short is one of the following
```
d days
w weeks
m months
p patches
```
Example: `2d` represents logs not older than 2 days.
### Alias
Names and short names for each player, class and boss are stored and can be changed by using `$alias` command. There are
3 types of queries for this command:
```
$alias <type>
$alias <type> <full_name>
$alias <type> <full_name> <new_short_name>
```
The first one will list all full and short names for that type of name where type is one of the flags `-b, -c, -pl`. 
The second one lists the current full and short name for that full name.
The last one updates the short_name (if it is not taken). Names are matched by short name so this is a way to make 
queries easier to write.

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
- Add queries on boons
- Code optimizations
  - Optimize deconstruction of data
  - Optimize DB calls