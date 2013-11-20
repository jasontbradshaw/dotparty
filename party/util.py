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

def ensure_python_version():
  '''Ensure that we're using the minimum required Python version.'''

  # TODO: determine the actual required version
  if sys.version_info < (2, 6):
    raise ValueError("dotparty requires Python version 2.6 or later!")
