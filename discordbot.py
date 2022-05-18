from discord.ext import commands

import botcommands
from discordtoken import get_discord_token


class LogBot:
    def __init__(self):
        self.bot = commands.Bot(command_prefix="$")
        self.token = get_discord_token()
        self.prepare_bot()

    def run(self):
        @self.bot.event
        async def onRead():
            print(self.bot.user.name, "has connected to the server")

        self.bot.run(self.token)

    def prepare_bot(self):
        @self.bot.command(name='log')
        async def insert_logs(ctx, *args):
            await ctx.message.delete()
            await ctx.send("Inserting logs...")
            #botcommands.log_command(ctx, args)
            for log_link in args:
                print(log_link)

            await ctx.send("Done inserting logs")


        @self.bot.command(name='dur')
        async def query_duration(ctx, *args):
            pass

        @self.bot.command(name='dps')
        async def query_dps(ctx, *args):
            pass

        @self.bot.command(name='boon')
        async def query_boon(ctx, *args):
            pass
