from datetime import datetime
import os
import sys

import settings
import discord
import message_handler
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from events.base_event import BaseEvent
from events import *
from multiprocessing import Process

load_dotenv()

# Set to remember if the bot is already running, since on_ready may be called
# more than once on reconnects
this = sys.modules[__name__]
this.running = False

# Scheduler that will be used to manage events
sched = AsyncIOScheduler()


###############################################################################


def main():
    # Initialize the client
    print("Starting up...")
    client = discord.Client()

    # Define event handlers for the client
    # on_ready may be called multiple times in the event of a reconnect,
    # hence the running flag
    @client.event
    async def on_ready():
        if this.running:
            return

        this.running = True

        # Set the playing status
        if settings.NOW_PLAYING:
            print("Setting NP game", flush=True)
            await client.change_presence(activity=discord.Game(name=settings.NOW_PLAYING))
        print("Logged in!", flush=True)

        # Load all events
        print("Loading events...", flush=True)
        n_ev = 0
        for ev in BaseEvent.__subclasses__():
            event = ev()
            sched.add_job(
                event.run,
                event.trigger_mode,
                (client,),
                next_run_time=datetime.now(),
                **event.kwargs,
            )
            n_ev += 1
        sched.start()
        print(f"{n_ev} events loaded", flush=True)

    # The message handler for both new message and edits
    async def common_handle_message(message):
        text = message.content
        command_prefix = settings.COMMAND_PREFIX[os.environ.get("ENV")]
        if text.startswith(command_prefix) and text != command_prefix:
            cmd_split = text[len(command_prefix) :].split()
            try:
                await message_handler.handle_command(cmd_split[0].lower(), cmd_split[1:], message, client)
            except:
                print("Error while handling message", flush=True)
                raise

    @client.event
    async def on_message(message):
        await common_handle_message(message)

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)

    # Finally, set the bot running
    client.run(os.environ.get("BOT_TOKEN"))


###############################################################################


if __name__ == "__main__":
    main()
