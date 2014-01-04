from __future__ import unicode_literals

import errno
import glob
import os
import re
import shutil
import sys

# groups version numbers from strings like 'git version 1.8.3.2'
GIT_VERSION_REGEX = re.compile('(\d+(?:\.\d+)+)')

def mkdir(path, mode=0o0755):
  '''Create a directory, analogous to `mkdir -p`. mode defaults to 0755.'''

  try:
    os.makedirs(path, mode)
  except OSError, e:
    if e.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise

def rm(path, force=False):
  '''
  Remove a file. If force is True, can also remove a directory. Doesn't complain
  about non-existent directories.
  '''

  try:
    # try to remove it as a simple file
    os.remove(path)
  except OSError, e:
    # if we're not forcing, fail
    if not force and e.errno != errno.ENOENT:
      raise

    # attempt to remove it as a directory if the error wasn't caused by the
    # directory not existing.
    if e.errno != errno.ENOENT:
      try:
        shutil.rmtree(path)
      except OSError, e:
        # only raise the exception if it's NOT a non-existence exeption, since
        # force implies that we don't care.
        if e.errno != errno.ENOENT:
          raise

def cp(src, dest, recursive=False):
  '''Copy a file, or directory tree if recursive is True. Copys permissions.'''
  if recursive and os.path.isdir(src):
    shutil.copytree(src, dest)
  else:
    shutil.copy2(src, dest)

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

def toggle_hidden(path, hide):
  '''Turn a path into a hidden file.'''

  parts = list(os.path.split(path))

  # remove any leading dot from the file
  base = parts.pop()
  base = base[1:] if base[0] == '.' else base

  # add the dot back if we're hiding the file
  if hide:
    base = '.' + base

  # put the base back on the parts list and return the joined path
  parts.append(base)
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
    rm(link_dest, force=True)

  # create the link and all the directories needed to contain it
  mkdir(os.path.dirname(link_dest))
  os.symlink(src, link_dest)

def is_descendant(child, parent):
  '''Returns True if child is a descendant directory of parent, else False.'''
  common_prefix = os.path.commonprefix((parent, child))
  return common_prefix == parent

def ensure_version(prog, min_version, version):
  '''
  Ensure that the version tuple exceeds the min_version tuple, otherwise raise a
  ValueError.
  '''

  if version < min_version:
    msg = 'dotparty requires {0} version {1} or later to function, found {2}'
    msg = msg.format(prog,
      '.'.join(map(unicode, min_version)),
      '.'.join(map(unicode, version)),
    )
    raise ValueError(msg)

def ensure_python_version(min_version=(2,7)):
  '''Ensure that we're using the minimum required Python version.'''
  ensure_version('Python', min_version, sys.version_info)

def ensure_git_version(min_version=(1, 8)):
  '''Ensure that we have access to the minimum required Git version.'''

  # TODO: determine what the minimum supported Git version is

  try:
    from sh import git
  except ImportError:
    raise ValueError("'git' is required for dotparty to function")

  # parse out the version info
  raw = git.version().strip()
  match = GIT_VERSION_REGEX.search(raw)

  if not match:
    print match
    raise ValueError("Could not parse version info from output: '%s'" % raw)

  # parse the version match like "1.2.3.4" into a tuple like (1, 2, 3, 4)
  version = tuple(int(i) for i in match.group(1).split('.'))
  ensure_version('Git', min_version, version)

def ensure_required_software():
  '''Make sure that we have access to all the required software/versions.'''
  ensure_python_version()
  ensure_git_version()
