def convert_input(args):
    input = {'boss' : args[0]}
    for i in range(1, len(args), 2):
        input[args[i]] = args[i + 1]

    return input

def upload_log(log_link):


def prepare_context(ctx, message):
    await ctx.message.delete()
    await ctx.send(message)

def log_command(ctx, args):
    prepare_context(ctx, "Inserting logs...")
    for i in range(1, len(args), 1):
        upload_log(args[i])

    await ctx.send("Done")