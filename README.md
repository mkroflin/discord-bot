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

## TODO
- Portability
  - use .env variables instead of importing constants.py
- Add queries on boons
- Run the bot on a remote server
  - Add docker files
  - Deploy CI/CD with Github and a (free) Cloud service
- Code optimizations
  - Optimize deconstruction of data
  - Optimize DB calls