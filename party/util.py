from __future__ import unicode_literals

import glob
import os
import sys

import constants

def to_list(*values):
  '''
  Given any number of values, return the first non-None one as a list. If that
  value is already a list, returns it unmodified, otherwise returns it as the
  only member of a new list. If none of the values is non-None, returns an empty
  list.
  '''

  for value in values:
    if value is not None:
      # return a single-item list, or the value if it's already a list
      if isinstance(value, list):
        return value
      return [value]

  return []

def normpath(path, absolute=False, root=None):
  '''Thoroughly normalize a path name, optionally as an absolute path.'''

  # join the path to the root directory if specified
  if root is not None:
    path = os.path.join(root, path)

  path = os.path.expanduser(path)
  path = os.path.normpath(path)
  path = os.path.normcase(path)

  if absolute:
    path = os.path.abspath(path)

  return path

def normalize_to_root(path, root):
  '''
  Normalize a path to some root directory. If it's absolute, only normalizes.
  '''

  is_absolute = os.path.isabs(path)
  root = None if is_absolute else root
  return normpath(path, absolute=is_absolute, root=root)

def is_hidden(path):
  '''Return True if the file is hidden, False otherwise.'''
  return os.path.basename(path).startswith('.')

def expand_globs(files, root=None):
  '''
  Expand a list of files that may include globs and return the de-duplicated and
  sorted result. Optionally rooted to some directory.
  '''

  expanded = set([])

  for f in files:
    f = normalize_to_root(f, root)

    # NOTE: if a pattern like '*foo' does not match, it will be added to the
    # result list verbatim. this shouldn't normally be a problem, but might
    # become one if anybody names their files things like '*foo'.
    for g in glob.iglob(f):
      expanded.add(normalize_to_root(g, root))
    else:
      expanded.add(f)

  return sorted(expanded)

def symlink(link_name, source, overwrite=None):
  '''
  Create a link at link_name that points to source.

  If `overwrite` is None, it only overwrites the destination file if it's
  already a link, otherwise it throws an error. If `overwrite` is True, if
  forces an overwrite. If it's False, it throws an error if any file exists at
  link_name.
  '''

  link_name = util.normpath(link_name)
  source = util.normpath(source)

  link_name_exists = os.path.exists(link_name)
  link_name_is_link = os.path.islink(link_name)

  # handle our error states
  error_msg = "Can't create link '%s', a %s with that name already exists!"
  if overwrite is False and link_name_exists:
    raise IOError(error_msg % (link_name, 'file'))
  elif overwrite is None and link_name_exists and not link_name_is_link:
    raise IOError(error_msg % (link_name, 'non-link file'))

  # create the link
  os.symlink(source, link_name)

def ensure_python_version(version=(2,7)):
  '''Ensure that we're using the minimum required Python version.'''

  if sys.version_info < version:
    msg = 'dotparty requires Python version {0} or later!'
    raise ValueError(msg.format('.'.join(version)))
