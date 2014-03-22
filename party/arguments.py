from __future__ import unicode_literals
from __future__ import print_function

import argparse

import constants
import dotparty
import util

def add_debug_argument(parser):
  '''Add a --debug flag to a parser.'''

  parser.add_argument(
    '--debug',
    action='store_true',
    help='enable debug output'
  )

def add_link_subparser(subparsers):
  p = subparsers.add_parser('link',
      help='link dotfiles into the destination directory')

  add_debug_argument(p)

  p.add_argument(
    '-f', '--force',
    action='store_true',
    help='overwrite existing files at link destinations'
  )

  p.add_argument(
    '-t', '--test',
    action='store_true',
    help="don't actually create destination links (useful for testing)"
  )

  p.set_defaults(command=dotparty.link)

def add_install_subparser(subparsers):
  p = subparsers.add_parser('install',
      help='install the current configured packages')

  add_debug_argument(p)

  p.add_argument(
    'package',
    help=('the package to install. Can be a short GitHub link (user/repo), '
        'or a fully-qualified Git repo URL.')
  )

  p.set_defaults(command=dotparty.install)

def add_manage_subparser(subparsers):
  p = subparsers.add_parser('manage',
      help=('copy a file to the dotpary directory, replace the original '
          'with a link, and add the new file to the repo (if possible)'))

  add_debug_argument(p)

  p.add_argument(
    'path',
    type=lambda p: util.normpath(p, absolute=True),
    help='the path to the source file to manage'
  )

  p.add_argument(
    '-f', '--force',
    action='store_true',
    help='overwrite any existing files in the dotparty directory'
  )

  p.set_defaults(command=dotparty.manage)

def add_update_subparser(subparsers):
  p = subparsers.add_parser('update',
      help='download updates to installed packages')

  add_debug_argument(p)

  p.add_argument(
    'package',
    nargs='*',
    help='the package(s) to update, all if none are specified'
  )

  p.set_defaults(command=dotparty.update)

def add_upgrade_subparser(subparsers):
  p = subparsers.add_parser('upgrade',
      help='upgrade dotparty to the latest version')
  add_debug_argument(p)
  p.set_defaults(command=dotparty.upgrade)

def parse(args=None, namespace=None):
  '''Set up our arguments and return the parsed namespace.'''

  p = argparse.ArgumentParser(prog='dotparty')

  add_debug_argument(p)

  p.add_argument(
    '--version',
    action='version',
    version=('%(prog)s version ' + '.'.join(map(str, constants.VERSION)))
  )

  subparsers = p.add_subparsers(title='commands')

  # add the commands available on the base argument parser
  add_link_subparser(subparsers)
  add_install_subparser(subparsers)
  add_manage_subparser(subparsers)
  add_update_subparser(subparsers)
  add_upgrade_subparser(subparsers)

  args = p.parse_args(args=args, namespace=namespace)
  return args
