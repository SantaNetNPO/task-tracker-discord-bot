import os

# The prefix that will be used to parse commands.
# It doesn't have to be a single character!
COMMAND_PREFIX = {"default": "!", "dev": ".", "prod": "!"}

ADMIN_ROLE_MENTION = "<@&890467951420014612>"

REACTION_WAIT_TIMEOUT = 60

# The now playing game. Set this to anything false-y ("", None) to disable it
NOW_PLAYING = "games with your life."

# Base directory. Feel free to use it if you want.
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
