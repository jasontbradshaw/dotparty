#!/usr/bin/env python

from __future__ import unicode_literals

import collections
import json
import os
import platform

from sh import git

import arguments
import color
import constants
import util

# NOTE: there's currently no try/except error checking since it clutters the
# code up mightily - it will be added once the overall structure settles down.

def load_machine_id(machine_file_path=constants.MACHINE_ID_PATH):
  '''
  Load the machine id, normalize it, and return it. If there's no machine id
  file, return the hostname of the system. If that's not available, return None.
  '''

  machine_id = None

  # use the machine file if it exists, otherwise fall back on the hostname
  if os.path.exists(machine_file_path):
    with open(machine_file_path) as f:
      machine_id = f.read().strip()
  elif platform.node() != '':
    machine_id = platform.node()

    # fix OSX hostnames returning '.local' at the end
    local_suffix = '.local'
    if machine_id.endswith(local_suffix):
      machine_id = machine_id[:-len(local_suffix)]

  return machine_id

def load_config(user_path=constants.USER_CONFIG_PATH,
    default_path=constants.DEFAULT_CONFIG_PATH):
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
    config['ignore'] = frozenset(default_config['ignore'] + user_config['ignore'])

  # expand globs in the ignored list and root them in the dotparty directory
  config['ignore'] = frozenset(
      util.expand_globs(config['ignore'], root=constants.DOTPARTY_DIR))

  # normalize the destination directory
  config['destination'] = util.normpath(config['destination'])

  # normalize all links to their long form
  config['links'] = normalize_links(config['links'], config['destination'])

  return config

def normalize_links(links, dest):
  '''De-sugar the link map and turn everything into its long form.'''

  assert isinstance(links, dict)

  normalized_links = {}
  for link, value in links.iteritems():
    # the fully-expanded version of all links we'll canonicalize the sugared
    # links to. for sugary examples, see `party-example.json`.
    machines = []
    paths = []

    # put simple path strings into the result paths
    if isinstance(value, basestring):
      paths.append(value)
    elif isinstance(value, list):
      # use the path list as the result paths
      paths = value
    elif isinstance(value, dict):
      # turn value into a defaultdict that returns None for absent keys
      value = collections.defaultdict(lambda: None, value)

      # convert the first value that's either a string or a list into a list
      paths = util.to_list(value['path'], value['paths'])
      machines = util.to_list(value['machine'], value['machines'])

    # make sure we actually got lists out of this process
    assert isinstance(machines, list)
    assert isinstance(paths, list)

    # if we didn't get a machine, normalize it to the current machine
    if len(machines) == 0:
      machines.append(load_machine_id())

    # if we didn't get a path, use the key name prefixed with a dot
    if len(paths) == 0:
      paths.append('.' + link)

    # ensure all the values we got are strings
    assert all(isinstance(f, basestring) for f in paths)
    assert all(isinstance(f, basestring) for f in machines)

    # normalize all destination paths to the destination directory
    paths = [util.normalize_to_root(p, dest) for p in paths]

    # store the normalized result for this link under its expanded path name
    normalized_links[util.normalize_to_root(link, constants.DOTPARTY_DIR)] = {
      'machines': frozenset(machines),
      'paths': frozenset(paths)
    }

  return normalized_links

def path_to_long_form(path, dest):
  '''
  Turn a path string into a long-form dict using 'machines' and 'paths'. The
  destination path will be hidden.
  '''

  # if we're turning the path into a dot file, rename it with a '.' in front
  path = util.make_hidden(path)
  path = util.normalize_to_root(os.path.basename(path), dest)

  return {
    'machines': frozenset([load_machine_id()]),
    'paths': frozenset([path])
  }

def init():
  '''
  Initialize dotparty on a new machine. Essentially an alias for:
    $ dotparty link
    $ dotparty install
  '''

def link(config):
  '''Link all files in the dotparty directory to their configured locations.'''

  # add all the files that are immediate children of the base directory, are not
  # hidden, are not ignored, and do not have a custom config.
  links = {}
  for path in os.listdir(constants.DOTPARTY_DIR):
    path = util.normalize_to_root(path, root=constants.DOTPARTY_DIR)

    is_hidden = util.is_hidden(path)
    is_ignored = path in config['ignore']
    has_custom_config = path in config['links']

    if not is_hidden and not is_ignored and not has_custom_config:
      links[path] = path_to_long_form(path, config['destination'])

  # add explicitly configured files, skipping those not meant for this machine
  machine_id = load_machine_id()
  for path, info in config['links'].iteritems():
    if machine_id in info['machines']:
      links[path] = info

  # link the files to their destination(s)
  for link, info in links.iteritems():
    for path in info['paths']:
      util.symlink(path, link)

  # return the resulting links, for good measure
  return links

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

def upgrade():
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
  #   instructions for the user to do their own update

def update(installed_packages=[], *packages):
  '''Update the specified (or all, by default) packages.'''

  # TODO:
  # - iterate over all packages in the installed list and pull them, updating
  #   them if their folders exist, installing otherwise
  # - do the whole stash/rebase/pop dance during the update

def main():
  # make sure the user has the correct python version installed
  util.ensure_python_version()

  # FIXME: remove this!
  from pprint import pprint as pp

  args = arguments.parse()

  config = load_config()

  print 'config:'
  pp(config)

  link(config)

if __name__ == '__main__':
  main()
