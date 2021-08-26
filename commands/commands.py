from commands.base_command import BaseCommand


# This is a convenient command that automatically generates a helpful
# message showing all available commands
class Commands(BaseCommand):
    def __init__(self):
        description = "Displays this help message"
        params = None
        alternate_names = ["help", "shakuni"]
        super().__init__(description, params, alternate_names)

    async def handle(self, params, message, client):
        COMMAND_HANDLERS = {}
        for c in BaseCommand.__subclasses__():
            COMMAND_HANDLERS[c.__name__.lower()] = c()

        # Displays all descriptions, sorted alphabetically by command name
        msg = ""
        for cmd in sorted(COMMAND_HANDLERS.items()):
            msg += "\n" + cmd[1].description

        await message.channel.send(msg)
