#!/usr/bin/env python

from __future__ import unicode_literals

# FIXME: remove this!
from pprint import pprint as pp

import os

from sh import git

import arguments
import color
import config
import constants
import util

# NOTE: there's currently no try/except error checking since it clutters the
# code up mightily - it will be added once the overall structure settles down.

def init(conf, args):
  '''
  Initialize dotparty on a new machine. Essentially an alias for:
    $ dotparty link
    $ dotparty install
  '''

def link(conf, args):
  '''Link all files in the dotparty directory to their configured locations.'''

  # add all the files that are immediate children of the base directory, are not
  # hidden, are not ignored, and do not have a custom config.
  links = {}
  for path in os.listdir(constants.DOTPARTY_DIR):
    path = util.normalize_to_root(path, root=constants.DOTPARTY_DIR)

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

    print msg

  # return the resulting links, for good measure
  return links

def install(conf, args):
  '''Clone a package to the bundle directory and add it to the config file.'''

  # TODO:
  # - determine whether we're dealing with a repo URL or a github reference
  # - build a URL if we weren't given one
  # - add the package to the config if --save is specifed
  # - clone it to the package directory

def manage(conf, args):
  '''
  Move a file to the base directory and create a link pointing to its original
  location.
  '''

  # TODO:
  # - check if the file is an already-managed link, bail if so
  # - move the file to the base directory
  # - create a link in its original location pointing to its new location
  # - add and commit it to the repo with a standard message

def upgrade(conf, args):
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

def update(conf, args):
  '''Update the specified (or all, by default) packages.'''

  # TODO:
  # - iterate over all packages in the installed list and pull them, updating
  #   them if their folders exist, installing otherwise
  # - do the whole stash/rebase/pop dance during the update

def main():
  # make sure the user has the correct python version installed
  util.ensure_python_version()
  util.ensure_git_version()

  args = arguments.parse()
  conf = config.load_config()

  # call the subcommand the user specified with the config and arguments
  args.command(conf, args)

if __name__ == '__main__':
  main()
