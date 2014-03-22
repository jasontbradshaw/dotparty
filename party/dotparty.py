#!/usr/bin/env python

from __future__ import unicode_literals
from __future__ import print_function

# FIXME: remove this!
from pprint import pprint as pp

import json
import os
import shutil
import sys

from sh import git

import arguments
import color
import config
import constants
import util

def link(conf, args):
  '''Link all files in the dotparty directory to their configured locations.'''

  # load our machine id so we know which files to link
  machine_id = config.get_machine_id()

  # map all file paths to their destination configs for this machine
  links = {}
  for path in os.listdir(constants.DOTPARTY_DIR):
    path = util.normalize_to_root(path, constants.DOTPARTY_DIR)

    is_hidden = util.is_hidden(path)
    is_ignored = path in conf['ignore']

    if not is_hidden and not is_ignored:
      # load the config for the given path
      file_config = config.get_file_config(path, conf['destination'])

      # if the file belongs on this machine, store its config
      if config.machine_matches(machine_id, file_config['machines']):
        links[path] = file_config

  # find the longest link basename for pretty output formatting
  max_src_width = max(len(os.path.basename(k)) for k in links.keys())
  link_symbol = ' -> '

  # link the files to their destination(s)
  for src, info in links.iteritems():
    msg = os.path.basename(src).rjust(max_src_width)
    msg += color.grey(link_symbol)

    for i, dest in enumerate(info['paths']):
      # the color of the link destination, different when we're creating a new
      # link, overwriting a link, and overwriting a normal file.
      dest_color = 'green'
      if os.path.lexists(dest):
        dest_color = 'cyan'
        if not os.path.islink(dest):
          dest_color = 'yellow'

      # do the symlink unless we're doing a dry run
      if not args.test:
        # overwrite links only by default, everything if forcing
        overwrite = True if args.force else None
        util.symlink(dest, src, overwrite=overwrite)

      # pad the left space if we're not the first item, since items with
      # multiple destinations are all under the same link name and symbol.
      if i > 0:
        msg += os.linesep
        msg += ' ' * (max_src_width + len(link_symbol))

      msg += color.colored(dest, dest_color)

    print(msg)

  # return the created links for good measure
  return links

def install(conf, args):
  '''Clone a package to the packages directory.'''

  # TODO:
  # - determine whether we're dealing with a repo URL or a github reference
  # - build a URL if we weren't given one
  # - add the package to the config if --save is specified
  # - clone it to the package directory

def manage(conf, args):
  '''
  Move a file to the base directory and leave a link pointing to its new
  location in its place.
  '''
  # bail if the file is already a link
  if os.path.islink(args.path):
    raise ValueError('Unable to manage ' + color.cyan(args.path) +
        " since it's already a link!")

  # make sure the path is a descendant of the destination directory
  if not util.is_descendant(args.path, conf['destination']):
    raise ValueError("Unable to manage files that aren't descendants of " +
        'the destination directory (' + color.cyan(conf['destination']) + ')')

  # mark files that aren't direct descendants of the root as such
  unrooted = os.path.dirname(args.path) != conf['destination']

  # get the path of the file if it will be copied into the dotparty directory
  dest_path = os.path.join(constants.DOTPARTY_DIR, os.path.basename(args.path))

  # rename the file as appropriate to to its original name
  dest_path, config_file_path = config.configify_file_name(dest_path)

  # give unrooted files a config file path so they'll go to the correct place
  if unrooted and config_file_path is None:
    config_file_path = util.toggle_hidden(dest_path, True)

  # bail if the file is already managed and we're not overwriting
  dest_exists = os.path.exists(dest_path)
  config_exists = (config_file_path is not None and
      os.path.exists(config_file_path))
  if (dest_exists or config_exists) and not args.force:
    raise ValueError("Can't manage " + color.cyan(args.path) +
        " since it already appears to be managed (use --force to override)")

  # create a file config if necessary
  # replace any existing dest file with a copy of the new one
  util.rm(dest_path, force=True)
  util.cp(args.path, dest_path, recursive=True)

  # replace any existing config file with our new one
  if config_file_path is not None:
    util.rm(config_file_path, force=True)

    # build a config for this file
    file_config = config.normalize_file_config({
      'paths': [args.path],
    }, conf['destination'])

    # create a config file from our config dict
    with open(config_file_path, 'w') as f:
      json.dump(file_config, f, indent=2)

  # create a link to the new location, overwriting the old file
  util.symlink(args.path, dest_path, overwrite=True)

  print(color.cyan(args.path), 'copied and linked')

  # TODO:
  # - add and commit the file to the repo if --save is specified
  # - modify the config for the new file if necessary

  # # move us to the current dotparty directory so all git commands start there
  # os.chdir(constants.DOTPARTY_DIR)

  # # alert the user if we have uncommitted changes (git exits non-0 in this case)
  # if git.diff(exit_code=True, quiet=True, _ok_code=(0, 1)).exit_code != 0:
  #   print('dotparty repo has uncommitted changes - the newly-managed file',
  #       'will have to be added to the repo manually', file=sys.stderr)

def update(conf, args):
  '''Apply dotparty updates from the upstream repository.'''

  print('Checking for updates...')

  # fetch changes from the canonical repo
  git.fetch(constants.DOTPARTY_REMOTE, no_tags=True)

  # get a list of the commit messages for the incoming changes
  updates = git.log('..FETCH_HEAD', oneline=True).splitlines()
  updates = tuple(m.split(None, 1) for m in updates)

  # print out a list of the incoming updates
  if len(updates) > 0:
    print('There are updates available:')

    max_updates = 10
    for commit, msg in updates[:max_updates]:
      print(color.yellow('*'), msg)

    # print a special message if too many updates are available
    if len(updates) > max_updates:
      print('...and %d more!' % (len(updates) - max_updates))
      print('Run `git log ..FETCH_HEAD` to see the full list')
  else:
    print('Already up-to-date!')

  # TODO:
  # - stash current modifications to the repo
  # - squash rebase the updates on top as a single commit (for a nice history)
  # - attempt to un-stash the changes
  # - if rebase failed, roll back to the pre-update state and complain with
  #   instructions for the user to do their own update

def upgrade(conf, args):
  '''Upgrade the specified (or all, by default) packages.'''

  # TODO:
  # - iterate over all packages in the installed list and pull them, updating
  #   them if their folders exist, installing otherwise
  # - do the whole stash/rebase/pop dance during the update

def main():
  # make sure the user has the correct versions of required software installed
  util.ensure_required_software()

  args = arguments.parse()
  conf = config.load_config()

  # call the subcommand the user specified with the config and arguments
  try:
    args.command(conf, args)
  except Exception as e:
    # raise the full exeption if debug is enabled
    if args.debug:
      raise

    # if we encounter an exception, print it and exit with an error
    print(color.red('[error]'), e, file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
  main()
