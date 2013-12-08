import os

import util

# where the dotparty remote lives, and what it should be called
DOTPARY_REMOTE = ('dotparty', 'https://github.com/jasontbradshaw/dotparty.git')

# the directory that the dotparty script lives in
# NOTE: these assume that these files are within the script directory!
SCRIPT_DIR = os.path.dirname(util.normpath(__file__))
DOTPARTY_DIR = os.path.dirname(util.normpath(os.path.join(__file__, '../')))

MACHINE_ID_FILE_PATH = util.normpath("~/.party-machine")
USER_CONFIG_PATH = util.normpath("~/.party.json")
DEFAULT_CONFIG_PATH = util.normpath(
    os.path.join(SCRIPT_DIR, "party-default.json"))
