from __future__ import unicode_literals

import collections
import os

import util

# the current version of dotparty
VERSION = (0, 0, 0)

# the git remote where the dotparty repository lives. used for updating dotparty
# to the latest version.
GitRemote = collections.namedtuple('Remote', ['name', 'url'])
DOTPARY_REMOTE = GitRemote('dotparty',
    'https://github.com/jasontbradshaw/dotparty.git')

# the directories that the dotparty files and script live in
# NOTE: these assume that these files are within the script directory!
DOTPARTY_DIR = os.path.dirname(util.normpath(os.path.join(__file__, '../')))
SCRIPT_DIR = os.path.dirname(util.normpath(__file__))

# config file paths
MACHINE_ID_PATH = util.normpath('~/.party-machine')
USER_CONFIG_PATH = util.normpath('~/.party.json')
DEFAULT_CONFIG_PATH = util.normpath(
    os.path.join(SCRIPT_DIR, 'party-default.json'))
