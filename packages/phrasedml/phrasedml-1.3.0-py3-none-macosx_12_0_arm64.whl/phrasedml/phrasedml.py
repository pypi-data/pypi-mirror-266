# -*- coding: utf-8 -*-
"""
Created November 2021

@author: Lucian Smith
"""


##@Module phrasedmlPython
#This module allows access to the phrasedml library from python
import os
from ctypes import c_long, c_int, c_char_p, c_ulong, c_bool, c_double, POINTER, cdll
import inspect
import platform

# Ctypes will only load the dll properly if the working directory is the same as 
# the directory where the dll is (at least on Windows).
__thisfile = inspect.getframeinfo(inspect.currentframe()).filename
__libdir = os.path.dirname(os.path.abspath(__thisfile))
#print(__thisfile)
#print(__libdir)

__oldir = os.getcwd()
os.chdir(__libdir)

__osname = platform.system()
if __osname == "Windows":
   __sharedLib = os.path.join(__libdir, 'libphrasedml.dll')
elif __osname == "Linux":
   __sharedLib = os.path.join(__libdir, "libphrasedml.so")
elif __osname == "Darwin":
   __sharedLib = os.path.join(__libdir, "libphrasedml.dylib")

if not os.path.isfile(__sharedLib):
    print('Unable to find shared library file', __sharedLib, "Exiting.")
    exit()
else:
    pass
    #print(__sharedLib, 'found.')
__phrasedLib = cdll.LoadLibrary(__sharedLib)

os.chdir(__oldir)

#Definitions
__version__ = "1.1.0"

#Library functions
__phrasedLib.convertFile.restype = c_char_p
__phrasedLib.convertFile.argtypes = (c_char_p, )

def convertFile(filename):
   """
   Convert a file from phraSEDML to SEDML, or visa versa.  If NULL is returned, an error occurred, which can be retrieved with
   @if python
   getLastError()'.
   @else
   getLastPhrasedError()'.
   @endif

   @return The converted file, as a string.

   @param filename the filename as a character string.  May be either absolute or relative to the directory the executable is being run from.

   @if python
   @see getLastError()
   @else
   @see getLastPhrasedError()
   @endif
   """
   if type(filename) == str:
      filename = filename.encode('utf-8')
   ret = __phrasedLib.convertFile(filename)
   if ret==None:
      return ret
   return ret.decode('utf-8')


__phrasedLib.setWriteSEDMLTimestamp.restype = None
__phrasedLib.setWriteSEDMLTimestamp.argtypes = (c_bool, )

def setWriteSEDMLTimestamp(writeTimestamp):
   """
   Sets whether, when writing a SED-ML file, the timestamp is included.
   """
   __phrasedLib.setWriteSEDMLTimestamp(writeTimestamp)

__phrasedLib.setWorkingDirectory.restype = None
__phrasedLib.setWorkingDirectory.argtypes = (c_char_p, )

def setWorkingDirectory(directory):
   """
   Sets the working directory for phraSED-ML to look for referenced files.

   @param directory the directory as a character string.  May be either absolute or relative to the directory the executable is being run from.
   """
   if type(directory) == str:
      directory = directory.encode('utf-8')
   __phrasedLib.setWorkingDirectory(directory)

__phrasedLib.getLastPhraSEDML.restype = c_char_p
__phrasedLib.getLastPhraSEDML.argtypes = ()

def getLastPhraSEDML():
   """
   If a previous 'convert' call was successful, the library retains an internal representation of the SEDML and the PhraSEDML.  This call converts that representation to PhraSEDML and returns the value, returning an empty string if no such model exists.
   """
   ret = __phrasedLib.getLastPhraSEDML()
   if ret==None:
      return ret
   return ret.decode('utf-8')


__phrasedLib.getPhrasedWarnings.restype = c_char_p
__phrasedLib.getPhrasedWarnings.argtypes = ()

def getPhrasedWarnings():
   """
   When translating some other format to phraSEDML, elements that are unable to be translated are saved as warnings, retrievable with this function (returns NULL if no warnings present).
   """
   ret = __phrasedLib.getPhrasedWarnings()
   if ret==None:
      return ret
   return ret.decode('utf-8')


__phrasedLib.convertString.restype = c_char_p
__phrasedLib.convertString.argtypes = (c_char_p, )

def convertString(model):
   """
   Convert a model string from phraSEDML to SEDML, or visa versa.  If NULL is returned, an error occurred, which can be retrieved with
   @if python
   getLastError().
   @else
   getLastPhrasedError().
   @endif

   @return The converted model, as a string.

   @param model the model as a character string.  May be either SED-ML or phraSED-ML.

   @if python
   @see getLastError()
   @else
   @see getLastPhrasedError()
   @endif
   """
   if type(model) == str:
      model = model.encode('utf-8')
   ret = __phrasedLib.convertString(model)
   if ret==None:
      return ret
   return ret.decode('utf-8')


__phrasedLib.setReferencedSBML.restype = c_bool
__phrasedLib.setReferencedSBML.argtypes = (c_char_p, c_char_p, )

def setReferencedSBML(URI, sbmlstring):
   """
   Allows phrasedml to use the given SBML document as the filename, instead of looking for the file on disk.  If the document is invalid SBML, 'false' is returned, but the document is still saved.

   @param URI the string that, when used in phrasedml, should reference the @p sbmlstring.
   @param sbmlstring the SBML document string to use when the @p URI is encountered.

   @return a boolean indicating whether the document is valid SBML or not.  Either way, the document is saved as the reference document for the given filename string.
   """
   if type(URI) == str:
      URI = URI.encode('utf-8')
   if type(sbmlstring) == str:
      sbmlstring = sbmlstring.encode('utf-8')
   return __phrasedLib.setReferencedSBML(URI, sbmlstring)

__phrasedLib.clearReferencedSBML.restype = None
__phrasedLib.clearReferencedSBML.argtypes = ()

def clearReferencedSBML():
   """
   Clears and removes all referenced SBML documents.
   """
   __phrasedLib.clearReferencedSBML()

__phrasedLib.getLastPhrasedError.restype = c_char_p
__phrasedLib.getLastPhrasedError.argtypes = ()

def getLastError():
   """
   When any function returns an error condition, a longer description of the problem is stored in memory, and is obtainable with this function.  In most cases, this means that a call that returns a pointer returned 'NULL' (or 0).
   """
   ret = __phrasedLib.getLastPhrasedError()
   if ret==None:
      return ret
   return ret.decode('utf-8')


__phrasedLib.getLastPhrasedErrorLine.restype = c_int
__phrasedLib.getLastPhrasedErrorLine.argtypes = ()

def getLastErrorLine():
   """
   Returns the line number of the file where the last error was obtained, if the last error was obtained when parsing a phraSED-ML file.  Otherwise, returns 0.
   """
   return __phrasedLib.getLastPhrasedErrorLine()

__phrasedLib.freeAllPhrased.restype = None
__phrasedLib.freeAllPhrased.argtypes = ()

def freeAllPhrased():
   """
   Frees all pointers handed to you by libphraSEDML.
   All libphraSEDML functions above that return pointers return malloc'ed pointers that you now own.  If you wish, you can ignore this and never free anything, as long as you call 'freeAllPhrased' at the very end of your program.  If you free *anything* yourself, however, calling this function will cause the program to crash!  It won't know that you already freed that pointer, and will attempt to free it again.  So either keep track of all memory management yourself, or only use this function every time you want to clean up memory.

   Note that this function only frees pointers handed to you by other phrasedml_api functions.  The models themselves are still in memory and are available.  (To clear that memory, use clearPreviousLoads() )
   """
   __phrasedLib.freeAllPhrased()

__phrasedLib.getLastSEDML.restype = c_char_p
__phrasedLib.getLastSEDML.argtypes = ()

def getLastSEDML():
   """
   If a previous 'convert' call was successful, the library retains an internal representation of the SEDML and the PhraSEDML.  This call converts that representation to SEDML and returns the value, returning an empty string if no such model exists.
   """
   ret = __phrasedLib.getLastSEDML()
   if ret==None:
      return ret
   return ret.decode('utf-8')


__phrasedLib.addDotXMLToModelSources.restype = None
__phrasedLib.addDotXMLToModelSources.argtypes = (c_bool, )

def addDotXMLToModelSources(force=False):
   """
   Sometimes, a user may wish to input phrasedml with the name of a model, instead of an actual filename.  This is particularly true in Tellurium, where one model is defined by Antimony, and has no immediate filename.  When creating SED-ML, however, an actual file needs to be referenced.  As such, [modelname].xml is a more realistic filename to use than simply [modelname]--this function converts all such filenames in the model, and assumes that you are making similar changes to the files themselves.  If any filename already ends in ".xml" or in ".sbml", that filename will not be changed.  To retrieve the modified version, use getLastPhraSEDML() or getLastSEDML().
   """
   __phrasedLib.addDotXMLToModelSources(force)

