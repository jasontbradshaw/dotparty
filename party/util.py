import glob
import os
import sys

def normpath(path, absolute=False):
  '''Thoroughly normalize a path name, optionally as an absolute path.'''
  path = os.path.expanduser(path)
  path = os.path.normpath(path)
  path = os.path.normcase(path)

  if absolute:
    path = os.path.abspath(path)

  return path

def expand_globs(*files):
  '''
  Expand a list of files that may include globs and return the de-duplicated and
  sorted result.
  '''

  expanded = set([])

  for f in files:
    for g in glob.iglob(f):
      expanded.add(globs)
    else:
      expanded.add(i)

  return sorted(expanded)

def symlink(link_name, source, overwrite=None):
  '''
  Create a link at link_name that points to source.

  If `overwrite` is None, it only overwrites the destination file if it's already
  a link, otherwise it throws an error. If `overwrite` is True, if forces an
  overwrite. If it's false, it throws an error if any file exists at link_name.
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
