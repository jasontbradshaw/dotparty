from __future__ import unicode_literals

import collections
import json
import os
import platform

import constants
import util

# NOTE: there's currently no try/except error checking since it clutters the
# code up mightily - it will be added once the overall structure settles down.

def get_machine_id(machine_file_path=constants.MACHINE_ID_PATH):
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
      machines.append(get_machine_id())

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
  path = util.toggle_hidden(path, True)
  path = util.normalize_to_root(os.path.basename(path), dest)

  return {
    'machines': frozenset([get_machine_id()]),
    'paths': frozenset([path])
  }
