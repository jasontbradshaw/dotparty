#!/usr/bin/env python

import json
import os
import platform
import sys

import util

# NOTE: there's currently no try/except error checking since it clutters the
# code up mightily - it will be added once the overall structure settles down.

MACHINE_ID_FILE_PATH = util.normpath("~/.party-machine")
USER_CONFIG_PATH = util.normpath("~/.party.json")
DEFAULT_CONFIG_PATH = util.normpath("./party-default.json")

def load_machine_id(path=MACHINE_ID_FILE_PATH):
  '''
  Load the machine id, normalize it, and return it. If there's no machine id
  file, return the hostname of the system. If that's not available, return None.
  '''

  machine_id = None

  # use the machine file if it exists, otherwise fall back on the hostname
  if os.path.exists(path):
    with open(path) as f:
      machine_id = f.read().strip()
  elif platform.node() != '':
    machine_id = platform.node()

  return machine_id

def load_config(user_path=USER_CONFIG_PATH, default_path=DEFAULT_CONFIG_PATH):
  '''Load the default dotparty config file, then overlay the user's on top.'''

  # make sure we can load our default config file
  assert os.path.exists(default_path)

  # load the default config
  default_config = {}
  with open(default_path) as f:
    default_config = json.load(f)

  # load the user's config if one exists
  user_config = {}
  if os.path.exists(user_path):
    with open(user_path) as f:
      user_config = json.load(f)

  # build a final config of the default values custom-merged with the user's
  config = {}
  config.update(default_config)
  config.update(user_config)

  # use the user's ignored values in addition to, not instead of, ours. we need
  # this because we always need to ignore our own files, and it's cleaner to do
  # so through the normal ignore channel than to write custom checks everywhere.
  if 'ignore' in user_config:
    config[u'ignore'] = default_config['ignore'] + user_config['ignore']

  return config

def main(args):
  # FIXME: remove this!
  from pprint import pprint as pp

  machine_id = load_machine_id()
  config = load_config()

  print 'machine id:', machine_id
  print 'config: ', config

if __name__ == '__main__':
  main(sys.argv)
