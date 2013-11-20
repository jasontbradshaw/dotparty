#!/usr/bin/env python

import argparse
import json
import os
import platform

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

    # fix OSX hostnames returning '.local' at the end
    local_suffix = '.local'
    if machine_id.endswith(local_suffix):
      machine_id = machine_id[:-len(local_suffix)]

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
    config['ignore'] = default_config['ignore'] + user_config['ignore']

  return config

def parse_args():
  '''Set up our arguments and return the parsed namespace.'''

  p = argparse.ArgumentParser(prog='dotparty')

  # requires a command
  # one of:
  #   link
  #   install
  #   manage
  #   update
  #   upgrade
  p.add_argument('command', nargs=1, help='the command to run')

  return p.parse_args()

def link(src, dest, machine_id, locations):
  '''Link all the files in the directory to their configured locations.'''

  # TODO:
  # - find all the files that are immediate children of the base directory
  # - filter out the ignored files
  # - filter out files that specify another platform
  # - build a map of the remaining files to their locations
  # - link those files

def install(package_or_repo_url, save=False):
  '''Clone a package to the bundle directory and add it to the config file.'''

  # TODO:
  # - determine whether we're dealing with a repo URL or a github reference
  # - build a URL if we weren't given one
  # - add the package to the config if --save is specifed
  # - clone it to the package directory

def manage(path):
  '''
  Move a file to the base directory and create a link pointing to its original
  location.
  '''

  # TODO:
  # - check if the file is an already-managed link, bail if so
  # - move the file to the base directory
  # - create a link in its original location pointing to its new location
  # - add and commit it to the repo with a standard message

def update():
  '''Pull dotparty updates from the upstream repository.'''

  # TODO:
  # - see if there's an upstream ref that matches the canonical repo
  # - add a new ref if there isn't one, generating a random name if necessary
  # - fetch updates from the upstream ref
  # - list the changes, truncating the list if it's too long
  # - stash current modifications to the repo
  # - squash rebase the updates on top as a single commit (for a nice history)
  # - attempt to un-stash the changes
  # - if rebase failed, roll back to the pre-update state and complain with
  #   instructions so for user to do their own update

def upgrade(installed_packages=[], *packages):
  '''Upgrade the specified (or all, by default) packages.'''

  # TODO:
  # - iterate over all packages in the installed list and pull them, updating
  #   them if their folders exist, installing otherwise
  # - do the whole stash/rebase/pop dance during the update

def main():
  # make sure the user has the correct python version installed
  util.ensure_python_version()

  # FIXME: remove this!
  from pprint import pprint as pp

  args = parse_args()

  machine_id = load_machine_id()
  config = load_config()

  print 'args:', args
  print 'machine id:', machine_id
  print 'config: ', config

if __name__ == '__main__':
  main()
