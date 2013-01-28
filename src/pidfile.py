#!/usr/bin/python3
#-*- coding: utf-8 -*-
#
# Copyright (c) 2012, Fortuna a.s.
# All rights reserved
#
# DESCRIPTION
# PID file modul
#
# AUTHOR
#   Martin Vondra <vondra.martin@ifortuna.cz>
#
# History
#   2012-05-04
#       Porting to python3
#
#


"""
PidFile modul
Example:

from pidfile import PidFile

try:
    pid = PidFile("aplication.pid")
except PidFile.ProcessRunning as e:
    print(e);
    exit(-2)
#entry

"""

import os
import sys
import fcntl


class PidFile:
    """
    Pid file class
    """

    def __init__(self, path, forkSafe=0):
        self._path = path
        self._createdPID = 0
        self._pid = self.getCurrentPID()
        self.__openPIDFile()
        self.__setPID = 0
        if (not forkSafe):
            self.create()
    #endif


    def __openPIDFile(self):
        """
        Create PID file
        """
        if (self._createdPID):
            return 0
        #endif
        if os.path.exists(self._path):
            try:
                # file exists, try to open and lock file, get PID
                self._fd = os.open(self._path, os.O_RDWR | os.O_CREAT, 0o666)
                fcntl.lockf(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                pid = int(os.read(self._fd, 1024))
            except IOError as err:
                # file is locked by another process
                if err.errno == 11:
                    sf = open(self._path, "r")
                    try:
                        pid = int(sf.readline().strip())
                    except ValueError:
                        pid = "N/A"
                    #endtry
                    sf.close()
                    raise ProcessRunning(pid)
                #endif
            except (ValueError, TypeError):
                # can't open file or read PID from file.  File is probably
                # invalid or stale, so try to delete it.
                pid = None
                os.unlink(self._path)
            else:
                if self.pidRunning(pid):
                    raise ProcessRunning(pid)
                else:
                    try:
                        os.unlink(self._path)
                    except OSError:
                        # maybe the other process has just quit
                        # and has removed the file.
                        pass # try continuing...
                    #endtry
                #endif
            #endif
        #endif

        # save PID to the locked file
        self._pidfile = os.open(self._path, os.O_RDWR | os.O_CREAT, 0o666)
        fcntl.lockf(self._pidfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self._createdPID = 1
    #enddef


    def create(self):
        """
        Write PID to PID file
        """
        if (self.__setPID):
            return 0
        #endif
        os.write(self._pidfile, str(self._pid).encode("utf-8"))
        self.__setPID = 1
    #enddef


    def getCurrentPID(self):
        """
        Get PID for current proccess
        """
        return os.getpid()
    #enddef


    def pidRunning(self, pid):
        """
        Check if process is running
        @param pid process pid
        """
        try:
            os.kill(pid, 0)
        except OSError as e:
            if e.errno == 3: # No such process
                return 0
        #endtry
        return 1
    #enddef


    def __del__(self):
        self.remove()
    #enddef


    def remove(self):
        """
        Only remove the file if was created. Otherwise attempting to start
        a second process will remove the file created by the first.
        """
        if (self._createdPID and self.__setPID):
            try:
                os.close(self._pidfile)
                os.unlink(self._path)
            except OSError:
                pass
            #endtry
        #endif
    #enddef
#endclass


class ProcessRunning(Exception):
    """
    Indicate, that process is already running.
    """

    def __init__(self, pid):
        self.pid = pid
    #enddef


    def __str__(self):
        return repr(self)
    #enddef


    def __repr__(self):
        return ("<ProcessRunning: Process is already running, pid=%s>" % \
                self.pid)
    #enddef
#endclass
