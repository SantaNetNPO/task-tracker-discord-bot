from commands.base_command import BaseCommand

# This, in addition to tweaking __all__ on commands/__init__.py,
# imports all classes inside the commands package.
from commands import *

import settings

# Register all available commands
COMMAND_HANDLERS = {}
for c in BaseCommand.__subclasses__():
    obj = c()
    for alternate_name in c().alternate_names:
        COMMAND_HANDLERS[alternate_name] = obj
    COMMAND_HANDLERS[c.__name__.lower()] = obj

###############################################################################


async def handle_command(command, args, message, bot_client):
    # Check whether the command is supported, stop silently if it's not
    # (to prevent unnecesary spam if our bot shares the same command prefix
    # with some other bot)
    if command not in COMMAND_HANDLERS:
        return

    print(
        f"{message.author.name}: {settings.COMMAND_PREFIX}{command} " + " ".join(args)
    )

    # Retrieve the command
    cmd_obj = COMMAND_HANDLERS[command]
    if cmd_obj.params and len(args) < len(cmd_obj.params):
        await message.channel.send(message.author.mention + " Insufficient parameters!")
    else:
        await cmd_obj.handle(args, message, bot_client)
