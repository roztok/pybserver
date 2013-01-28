#!/usr/bin/python3
#-*- coding: utf-8 -*-


from rpcserver import RPCServerConfig
import psycopg2
import configparser

class Config(RPCServerConfig):
    """
    
    """
    def __init__(self):
        super().__init__()
        self.user = _User(self.getConfig())
        self.sql = _SQL(self.getConfig())
    #enddef
#endclass

class _User:
    
    def __init__(self, parser):
        self.username = parser.get("user", "username")
        self.email = parser.get("user", "email") 
    #enddef
#endclass


class _SQL:
    
    def __init__(self, parser):
        try:
            self.host = parser.get("sql", "host")
        except configparser.NoOptionError:
            self.host = "localhost"
        #endtry
        try:
            self.port = parser.getint("sql", "port")
        except configparser.NoOptionError:
            self.port = 5423
        #endtry
        self.database = parser.get("sql", "database")
        self.user = parser.get("sql", "user")
        self.password = parser.get("sql", "password")
        self.connection = None
    #enddef

    def getDB(self):
         if not self.connection:
             if self.host == "localhost":
                 self.connection = psycopg2.connect(database=self.database, 
                                                user=self.user,
                                                password=self.password)
             else:
                 self.connection = psycopg2.connect(host=self.host, port=self.port,
                                                database=self.database, 
                                                user=self.user,
                                                password=self.password)
         #endif
         return self.connection
    #enddef
#enddef

config = Config()
