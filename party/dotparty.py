#!/usr/bin/env python

from __future__ import unicode_literals
from __future__ import print_function

# FIXME: remove this!
from pprint import pprint as pp

import os
import shutil
import sys

from sh import git

import arguments
import color
import config
import constants
import util

# NOTE: there's currently no try/except error checking since it clutters the
# code up mightily - it will be added once the overall structure settles down.

def link(conf, args):
  '''Link all files in the dotparty directory to their configured locations.'''

  # add all the files that are immediate children of the base directory, are not
  # hidden, are not ignored, and do not have a custom config.
  links = {}
  for path in os.listdir(constants.DOTPARTY_DIR):
    path = util.normalize_to_root(path, constants.DOTPARTY_DIR)

    is_hidden = util.is_hidden(path)
    is_ignored = path in conf['ignore']
    has_custom_config = path in conf['links']

    if not is_hidden and not is_ignored and not has_custom_config:
      links[path] = config.path_to_long_form(path, conf['destination'])

  # add explicitly configured files, skipping those not meant for this machine
  machine_id = config.get_machine_id()
  for path, info in conf['links'].iteritems():
    if machine_id in info['machines']:
      links[path] = info

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

  # return the created links
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
  Move a file to the base directory and create a link pointing to its original
  location.
  '''

  # make sure the path is a descendant of the destination directory
  if not util.is_descendant(args.path, conf['destination']):
    raise ValueError("Unable to manage files that aren't descendants of " +
        'the destination directory (' + color.cyan(conf['destination']) + ')')

  # TODO: handle managing files that AREN'T in the root of the destination dir
  if os.path.dirname(args.path) != conf['destination']:
    raise ValueError("Unable to manage files that aren't direct descendants " +
        'of the destination directory (' + color.cyan(conf['destination']) + ')')

  # get the path of the file if it will be copied into the dotparty directory.
  # the managed file will NOT be hidden, even if the original was.
  dotparty_path = os.path.join(constants.DOTPARTY_DIR,
      os.path.basename(args.path))
  dotparty_path = util.toggle_hidden(util.normpath(dotparty_path), False)

  # bail if the file is already managed and we're not overwriting
  if os.path.exists(dotparty_path) and not args.force:
    raise ValueError("Can't manage " + color.cyan(args.path) +
        " since it already exists (use --force to override)")

  # remove the destination file since we'll be overwriting it
  util.rm(dotparty_path, force=True)

  # copy the file to its new location
  util.cp(args.path, dotparty_path, recursive=True)

  # create a link to the new location, overwriting the old file
  util.symlink(args.path, dotparty_path, overwrite=True)

  print(color.cyan(args.path), 'copied and linked')

  # TODO:
  # - add and commit the file to the repo

  # # move us to the current dotparty directory so all git commands start there
  # os.chdir(constants.DOTPARTY_DIR)

  # # alert the user if we have uncommitted changes (git exits non-0 in this case)
  # if git.diff(exit_code=True, quiet=True, _ok_code=(0, 1)).exit_code != 0:
  #   print('dotparty repo has uncommitted changes - the newly-managed file',
  #       'will have to be added to the repo manually', file=sys.stderr)

def upgrade(conf, args):
  '''Apply dotparty updates from the upstream repository.'''

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

def update(conf, args):
  '''Update the specified (or all, by default) packages.'''

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
  except Exception, e:
    # raise the full exeption if debug is enabled
    if args.debug:
      raise

    # if we encounter an exception, print it and exit with an error
    print(color.red('[error]'), e, file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
  main()
