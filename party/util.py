from __future__ import unicode_literals

import errno
import glob
import os
import shutil
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

def make_hidden(path):
  '''Turn a path into a hidden file.'''
  parts = list(os.path.split(path))
  parts[-1] = '.' + parts[-1]
  return os.path.join(*parts)

def expand_globs(files, root=None):
  '''
  Expand a list of files that may include globs and return the de-duplicated and
  sorted result. Optionally rooted to some directory.
  '''

  expanded = set([])

  for f in files:
    f = normalize_to_root(f, root)

    # NOTE: all patterns (like '*foo') will be added to the result list
    # verbatim. this shouldn't normally be a problem, but might become one if
    # anybody names their files things like '*foo'.
    for g in glob.iglob(f):
      expanded.add(normalize_to_root(g, root))
    else:
      expanded.add(f)

  return sorted(expanded)

def mkdirp(path, mode=0o0755):
  '''Create a directory, analogous to `mkdir -p`. mode defaults to 0755.'''

  try:
    os.makedirs(path, mode)
  except OSError, e:
    if e.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise

def symlink(link_dest, src, overwrite=None):
  '''
  Create a link at link_dest that points to source. If there are intermediate
  directories that need creating for the link destination, those are created as
  well.

  If `overwrite` is None, it only overwrites the destination file if it's
  already a link, otherwise it throws an error. If `overwrite` is True, if
  forces an overwrite. If it's False, it throws an error if any file exists at
  link_dest.
  '''

  link_dest = normpath(link_dest)
  src = normpath(src)

  link_dest_exists = os.path.lexists(link_dest)
  link_dest_is_link = os.path.islink(link_dest)

  # handle our error states
  error_msg = "Can't create link '%s', a %s with that name already exists!"
  if overwrite is False and link_dest_exists:
    raise IOError(error_msg % (link_dest, 'file'))
  elif overwrite is None and link_dest_exists and not link_dest_is_link:
    raise IOError(error_msg % (link_dest, 'non-link file'))

  # remove the link file, since at this point we're allowed to in all cases
  if link_dest_exists:
    try:
      # try to remove it as a simple file
      os.remove(link_dest)
    except OSError, e:
      try:
        shutil.rmtree(link_dest)
      except OSError, e:
        raise

  # create the link and all the directories needed to contain it
  mkdirp(os.path.dirname(link_dest))
  os.symlink(src, link_dest)

def ensure_python_version(version=(2,7)):
  '''Ensure that we're using the minimum required Python version.'''

  if sys.version_info < version:
    msg = 'dotparty requires Python version {0} or later!'
    raise ValueError(msg.format('.'.join(version)))
