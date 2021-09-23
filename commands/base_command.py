import os
import settings

# Base command class
# Do not modify!


class BaseCommand:
    def __init__(self, description, params, alternate_names):
        self.name = type(self).__name__.lower()
        self.params = params
        self.alternate_names = alternate_names

        command_prefix = settings.COMMAND_PREFIX[os.environ.get("ENV")]
        desc = f"**{command_prefix}{self.name}**"

        if self.alternate_names:
            desc += f" (also: {command_prefix}{f', {command_prefix}'.join(self.alternate_names)})"

        if self.params:
            desc += " " + " ".join(f"*<{p}>*" for p in params)

        desc += f": {description}."
        self.description = desc

    # Every command must override this method
    async def handle(self, params, message, client):
        raise NotImplementedError  # To be defined by every command
