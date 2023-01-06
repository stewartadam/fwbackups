"""
fwbackups package initialization.
"""
import os
import sys
import subprocess

from threading import Thread, Event
from .i18n import encode


__author__ = "Stewart Adam <s.adam@diffingo.com>"
__status__ = "beta"
__version__ = "1.43.6" # FIXME
__license__ = "GNU GPLv2+"


class fwbackupsError(Exception):
  """A generic Exception for the program."""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def escapeQuotes(string, noQuotes):
  """Escapes quotes in string. noQuotes (1 or 2) defines which type of quote to
  escape. If 3 is passed, then both double and single quotes will be escaped
  (use with caution)."""
  if noQuotes not in [1,2,3]:
    raise ValueError('noQuotes must be and integer of 1 or 2')
  if noQuotes in [1, 3]:
    string = string.replace("'", "'\\''")
  if noQuotes == [2, 3]:
    string = string.replace('"', '\\"')
  return string

def execute(command, env=None, shell=False, stdoutfd=None):
  """Execute a command, wait for it to finish"""
  sub = subprocess.Popen(encode(command), stdin=subprocess.PIPE, stdout=stdoutfd, stderr=subprocess.PIPE, shell=shell, env=env)
  return sub.wait(), sub.stdout, sub.stderr

def executeSub(command, env=None, shell=False, stdoutfd=None):
  """Execute a command in the background"""
  sub = subprocess.Popen(encode(command), stdin=subprocess.PIPE, stdout=stdoutfd, stderr=subprocess.PIPE, shell=shell, env=env, text=True)
  return sub

def kill(PID, signal):
  """Effectively kill a process (win32 too!)"""
  # Thank you cookbook...
  # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/347462

  # IF we run Windows...
  if sys.platform == "win32":
    # ... Then use ctypes to kill it
    import ctypes
    PROCESS_TERMINATE = 1
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, PID)
    ctypes.windll.kernel32.TerminateProcess(handle, -1)
    return ctypes.windll.kernel32.CloseHandle(handle)
  # IF not...
  else:
     # ... Then do things the normal way! :D
     return os.kill(PID, int(signal))

def CheckPerms(path, mustExist=False):
  """Checks for read and write permissions."""
  read = CheckPermsRead(path, mustExist)
  write = CheckPermsWrite(path, mustExist)
  if read == True and write == True:
      return True
  return False

def CheckPermsRead(path, mustExist=False):
  """Checks for read permissions."""
  path = encode(path)
  if not os.path.exists(path) and not mustExist:
    path = os.path.dirname(path)
  return os.access(path, os.R_OK)

def CheckPermsWrite(path, mustExist=False):
  """Checks for write permissions."""
  path = encode(path)
  if not os.path.exists(path) and not mustExist:
    path = os.path.dirname(path)
  return os.access(path, os.W_OK)

class FuncAsThread(Thread):
  """Run a function as a new thread."""
  def __init__(self, functorun, args):
    Thread.__init__(self)
    self.__args = args
    self.__functorun = functorun
    self.retval = None
    self.traceback = None
    self.exception = None

  def run(self):
    try:
      retval = self.__functorun(*self.__args)
      self.retval = retval
    except SystemExit:
      # cancelled
      self.retval = -2
    except: # catch all other (non-request-for-cancel) exceptions
      # NOTE: Thread dies as soon as it gets the exception, so retval will be
      # None. Solution is to use "while thread.retval == None" rather than
      # "isAlive()" while checking for a return value.
      import traceback
      (etype, value, tb) = sys.exc_info()
      self.traceback = ''.join(traceback.format_exception(etype, value, tb))
      try:
        self.exception = etype(value)
      except:
        self.exception = etype
      self.retval = -1
    return self.retval

def runFuncAsThread(functorun, *kargs):
  """Runs a function as a new thread"""
  thread = FuncAsThread(functorun, kargs)
  thread.start()
  return thread

def getPyCronDir():
  import winreg
  try:
    k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Python Cron Service_is1")
  except EnvironmentError:
    print("You must install PyCron to run this program.")
    print("Press any key to continue")
    sys.exit(1)
  cronDir = winreg.QueryValueEx(k, "InstallLocation")[0]
  return cronDir
