from __future__ import unicode_literals

import collections
import json
import os
import platform

import constants
import util

def get_machine_id(machine_file_path=constants.MACHINE_ID_PATH):
  '''
  Load the machine id, normalize it, and return it. If there's no machine id
  file, return the hostname of the system. If that's not available, return None.
  '''

  machine_id = None

  # use the machine file if it exists, otherwise fall back on the hostname
  if os.path.exists(machine_file_path):
    with open(machine_file_path) as f:
      machine_id = json.load(f)['id']
  elif platform.node() != '':
    machine_id = platform.node()

    # fix OSX hostnames returning '.local' at the end
    local_suffix = '.local'
    if machine_id.endswith(local_suffix):
      machine_id = machine_id[:-len(local_suffix)]

  return machine_id

def machine_matches(machine_id, machines):
  '''
  Test a machine id against a list of machines, and return whether the given id
  matches against the list.

  A machine matches if either the machines list is empty (indicating 'all
  machines'), or the given id exists in the machines list.
  '''

  return len(machines) == 0 or machine_id in machines

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

  # build a config of the default values custom-merged with the user's
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
      util.expand_globs(config['ignore'], root=constants.REPO_DIR))

  # normalize the destination directory
  config['destination'] = util.normpath(config['destination'])

  # TODO: handle packages

  return config

def get_config_path(path):
  '''Return the config file name for a given path.'''
  base, name = os.path.split(path)
  hidden_name = util.toggle_hidden(name, True)
  return os.path.join(base, hidden_name)

def normalize_file_config(config, dest):
  '''Turn a file config into a normalized variant.'''

  # an empty config with all the expected keys
  result = {
    'paths': [],
    'machines': [],
  }

  if 'paths' in config:
    # normalize all paths names to our destination directory
    paths = [util.normalize_to_root(p, dest) for p in set(config['paths'])]
    result['paths'] = sorted(paths)

  if 'machines' in config:
    result['machines'] = sorted(frozenset(config['machines']))

  return result

def load_file_config_file(path, dest):
  '''
  Load the config for the given path if it exists, otherwise return None.

  Config File Format
  ----

  ```json
  {
    "machines": [
      "machineid1",
      "machineid2"
    ],

    "paths": [
      "relative/path/1",
      "relative/path/2"
    ]
  }
  ```

  Keys may be omitted, but beware: an empty `paths` list will result in the
  file never being linked!
  '''

  # if a config file exists, return its JSON contents
  config_path = get_config_path(path)
  if os.path.isfile(config_path):
    config = None
    with open(config_path, 'r') as f:
      return normalize_file_config(json.load(f), dest)

  # otherwise, signal that no file existed
  return None

def parse_file_config(path, dest):
  '''
  Parse the given file name and return a normalized config.

  Naming Rules
  ----

  * First leading '_' is replaced with a '.'.
  * When split on '@', every part excluding the first is treated as a machine id
  on which to link the given file.
  * Any file named the same as the local file preceded by a '.' is treated as a
    special config file for that local file.
  * Any of these rules may be combined.
  * A config file overrides all name modifiers, no matter what.
  * Any file that contains the '@' character or a leading '_' will need to have
    a compatible name and a corresponding config file to work. The rationale is
    that this is a very uncommon situation, so we don't bother accomodating it.
  '''

  # get the file name for the given path
  raw_name = os.path.basename(path)

  # determine if we need to add a leading dot to the destination, then remove it
  # from the name if present.
  is_hidden = raw_name[0] == constants.DOT_CHARACTER
  if is_hidden:
    raw_name = raw_name[1:]

  # attempt to find machine ids
  parts = raw_name.split(constants.MACHINE_SEPARATOR_CHARACTER)

  # build the final base name
  name = util.toggle_hidden(parts[0], is_hidden)

  # get the remaining machine ids
  machine_ids = parts[1:]

  config = {
    'paths': [name],
    'machines': machine_ids,
  }

  return normalize_file_config(config, dest)

def configify_file_name(path):
  '''
  Given a path, name it and its config file appropriately for our config naming
  scheme. If no config file is necessary, None is used instead. Returns a tuple
  of the new name and the config file name.
  '''

  base, name = os.path.split(path)

  # determine whether our path name is clean or not
  is_clean = not (name.startswith(constants.DOT_CHARACTER) or
      constants.MACHINE_SEPARATOR_CHARACTER in name)

  # always un-hide the name
  name = util.toggle_hidden(name, False)
  config_file_name = None

  if is_clean:
    # add our dot character if the file was originally hidden
    if util.is_hidden(path):
      name = constants.DOT_CHARACTER + name
  else:
    # otherwise, set the config file to the hidden version of the name
    config_file_name = util.toggle_hidden(name, True)

  configified_path = os.path.join(base, name)
  config_file_path = None
  if config_file_name is not None:
    config_file_path = os.path.join(base, config_file_name)

  return (configified_path, config_file_path)

def get_file_config(path, dest):
  '''
  Return a normalized config for the given path. If a config file exists for the
  given path, returns its contents instead and skips parsing.
  '''

  # normalize our path to the destination directory first
  path = util.normalize_to_root(path, dest)

  # immediately return the config as written if one exists
  config = load_file_config_file(path, dest)
  if config is not None:
    return config

  # otherwise, parse and return the file name itself
  return parse_file_config(path, dest)
