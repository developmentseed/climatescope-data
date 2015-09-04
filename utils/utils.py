# Climatescope utils

import json
import os.path
import shutil


def check_dir(d):
  """Check if a folder (d) exists. If so, ask user to delete it first.
  """
  if os.path.exists(d):
    print 'The directory \'%s\' seems to exist already. Please remove it and run this script again.' % (d)
    return True
  else:
    return False


def check_create_folder(d):
  """ Check whether a folder exists, if not the folder is created.

  :param d:
    Path to the folder
  :type d:
    String

  :returns:
    (String) the path to the folder
  """
  if not os.path.exists(d):
    os.makedirs(d)


def clean_dir(d, full = False):
  """Clean up a directory

  :param d:
    Path to folder
  :type d:
    String
  :param full:
    If full is set to True, the directory itself will be deleted
    as well.
  :type full:
    Boolean
  """
  if full:
    shutil.rmtree(d)
  else:
    for fn in os.listdir(d):
      file_path = os.path.join(d, fn)
      try:
        os.unlink(file_path)
      except Exception, e:
        print e


def write_json(f,data):
  """Write data to a json file

  :param f:
    Path to the file
  :param f:
    String
  :param data:
    Data to write to the file
  """
  with open(f ,'w') as ofile:
    json.dump(data, ofile)
