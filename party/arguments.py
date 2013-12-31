from __future__ import unicode_literals

import argparse

def add_init_subparser(subparsers):
  p = subparsers.add_parser('init',
      help='initialize a new computer with dotfiles')

def add_link_subparser(subparsers):
  p = subparsers.add_parser('link',
      help='link dotfiles into the destination directory')

def add_install_subparser(subparsers):
  p = subparsers.add_parser('install',
      help='install the current configured packages')

def add_manage_subparser(subparsers):
  p = subparsers.add_parser('manage',
      help='add a file to the repo, leaving a link in its place')

def add_update_subparser(subparsers):
  p = subparsers.add_parser('update',
      help='download updates to dotparty packages')

def add_upgrade_subparser(subparsers):
  p = subparsers.add_parser('upgrade',
      help='upgrade dotparty to the latest version')

def parse(args=None, namespace=None):
  '''Set up our arguments and return the parsed namespace.'''

  p = argparse.ArgumentParser(prog='dotparty')
  subparsers = p.add_subparsers()

  # add the commands available on the base argument parser
  add_init_subparser(subparsers)
  add_link_subparser(subparsers)
  add_install_subparser(subparsers)
  add_manage_subparser(subparsers)
  add_update_subparser(subparsers)
  add_upgrade_subparser(subparsers)

  return p.parse_args(args=args, namespace=namespace)
