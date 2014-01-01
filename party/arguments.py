from __future__ import unicode_literals

import argparse

import constants
import dotparty
import util

def add_init_subparser(subparsers):
  p = subparsers.add_parser('init',
      help='Initialize a new computer with dotfiles')

  p.add_argument(
    '-f', '--force',
    action='store_true',
    help='Overwrite existing files at link destinations'
  )

  p.set_defaults(command=dotparty.init)

def add_link_subparser(subparsers):
  p = subparsers.add_parser('link',
      help='Link dotfiles into the destination directory')

  p.add_argument(
    '-f', '--force',
    action='store_true',
    help='Overwrite existing files at link destinations'
  )

  p.add_argument(
    '-t', '--test',
    action='store_true',
    help="Don't actually create destination links (useful for testing)"
  )

  p.set_defaults(command=dotparty.link)

def add_install_subparser(subparsers):
  p = subparsers.add_parser('install',
      help='Install the current configured packages')

  p.add_argument(
    'package',
    type=util.normpath,
    help=('The package to install. Can be a short GitHub link (user/repo), '
        'or a fully-qualified Git repo URL.')
  )

  p.set_defaults(command=dotparty.install)

def add_manage_subparser(subparsers):
  p = subparsers.add_parser('manage',
      help='Move a file to the dotpary directory and leave a link in its place')

  p.add_argument(
    'path',
    type=util.normpath,
    help='The source file to manage'
  )

  p.add_argument(
    '-f', '--force',
    action='store_true',
    help='Overwrite any existing files in the dotparty directory'
  )

  p.set_defaults(command=dotparty.manage)

def add_update_subparser(subparsers):
  p = subparsers.add_parser('update',
      help='Download updates to installed packages')

  p.add_argument(
    'package',
    nargs='*',
    help='The package(s) to update, all if none are specified'
  )

  p.set_defaults(command=dotparty.update)

def add_upgrade_subparser(subparsers):
  p = subparsers.add_parser('upgrade',
      help='Upgrade dotparty to the latest version')
  p.set_defaults(command=dotparty.upgrade)

def parse(args=None, namespace=None):
  '''Set up our arguments and return the parsed namespace.'''

  p = argparse.ArgumentParser(prog='dotparty')

  p.add_argument(
    '--version',
    action='version',
    version=('%(prog)s version ' + '.'.join(map(unicode, constants.VERSION)))
  )

  subparsers = p.add_subparsers(title='commands')

  # add the commands available on the base argument parser
  add_init_subparser(subparsers)
  add_link_subparser(subparsers)
  add_install_subparser(subparsers)
  add_manage_subparser(subparsers)
  add_update_subparser(subparsers)
  add_upgrade_subparser(subparsers)

  args = p.parse_args(args=args, namespace=namespace)
  return args
