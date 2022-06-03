from discord.ext import commands
import botcommands


class LogBot:
    def __init__(self, config):
        print("INITIATING BOT...")
        self.bot = commands.Bot(command_prefix="$")
        self.token = config["DISCORD_TOKEN"]
        self.config = config
        self.prepare_bot()

    def run(self):
        @self.bot.event
        async def on_ready():
            print(self.bot.user.name, "has connected to the server")

        self.bot.run(self.token)

    def prepare_bot(self):
        @self.bot.command(name='log', help='Import list of logs (separated by whitespace)')
        async def insert_logs(ctx, *args):
            # await ctx.message.delete()
            await ctx.send("Inserting logs...")
            botcommands.log_command(args, self.config)
            await ctx.send("Done inserting logs")

        @self.bot.command(name='dur', help='Query boss phases by duration or start/end of a phase')
        async def query_duration(ctx, *args):
            await ctx.send("Calculating...")
            query, result = botcommands.dur_command(ctx, args, self.config)
            if query:
                await ctx.send("QUERY PARAMETERS: {}".format(query))
                await ctx.send(result)
            else:
                await ctx.send(result)

        @self.bot.command(name='dps', help='Query boss phases by dps or start/end dps of a phase')
        async def query_dps(ctx, *args):
            await ctx.send("Calculating...")
            query, result = botcommands.dps_command(ctx, args, self.config)
            if query:
                await ctx.send("QUERY PARAMETERS: {}".format(query))
                await ctx.send(result)
            else:
                await ctx.send(result)

        @self.bot.command(name='flags', help='List of all possible flags to use across other commands')
        async def query_flags(ctx, *args):
            await ctx.send(botcommands.flag_command())

        @self.bot.command(name='boon', help='Not implemented. For more information ask Tantor')
        async def query_boon(ctx, *args):
            pass

        @self.bot.command(name='alias', help='Look up and change alias for names')
        async def query_alias(ctx, *args):
            await ctx.send(botcommands.alias_command(args, self.config))

        @self.bot.command()
        @commands.is_owner()
        async def shutdown(context):
            exit()
