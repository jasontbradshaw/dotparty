import os

def normpath(path, absolute=False):
  '''Thoroughly normalize a path name, optionally as an absolute path.'''
  path = os.path.expanduser(path)
  path = os.path.normpath(path)
  path = os.path.normcase(path)

  if absolute:
    path = os.path.abspath(path)

  return path
