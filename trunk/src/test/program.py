#!/usr/bin/python3
#-*- coding: utf-8 -*-

import xmlrpc.client
from lib.config import config


def listClients(filters = {}, offset = 0, limit = None, criterion = "id", 
               direction = "asc"):
    """
    Vypise seznam klientu
    """    
    clients = [{"id" : 1001, "name" : "Fortuna a.s."}, 
              {"id" : 1002, "name" : "Pekarstvi Houska"},
              {"id" : 1003, "name" : "Tesar Triska"},
              {"id" : 1004, "name" : "Vaclav s.r.o."},
              {"id" : 1005, "name" : "Jan Zizka"},
              {"id" : 1006, "name" : "Frantisek Ferdinand"},
              {"id" : 1006, "name" : config.user.username}]
    
    return { "status" : 200, "statusMessage" : "OK", "clients" : clients }
#enddef


def client_getAttributes(clientId):
    """
    Provede soucet dvou celych cisel
    """
    if not isinstance(clientId, int):
        raise xmlrpc.client.Fault(-401, "Argument 'clientId' must be integer")
    #endif
    
    if clientId != 1001:
        return { "status" : 404, "statusMessage" : "Client not found" }
    #endif
        
    attr = {"id" : 1001, 
            "name" : "Fortuna a.s.", 
            "address" : "Jankovcova 1596/14b",
            "city" : "Praha",
            "zipCode" : "17000",
            "state" : "Czech Republic",
            "phoneNo" : "+420 267 218 111"}
    
    return { "status" : 200, "statusMessage" : "OK", \
            "clientAttributes" : attr }
#enddef


def client_create(attr):
    """
    """
    if not isinstance(attr, dict):
        raise xmlrpc.client.Fault(-401, "Argument 'clientAttributes'" \
                                  " must be dict.")
    #endif

    allowAttrs = ("name", "address", "city", "zipCode", "state", "phoneNo")
    
    for key in attr.keys():
        if key not in allowAttrs:
            raise xmlrpc.client.Fault(-401, "Argument '%s' is not allowed."\
                                      % key)
        #endif
        if not isinstance(attr[key], str):
              raise xmlrpc.client.Fault(-401, "Argument '%s' must be string."\
                                      % key)
        #endif
    #endfor
    
    return { "status" : 200, "statusMessage" : "OK", \
            "clientId" : 1001 }      
#enddef


def client_setAttributes(clientId, attr):
    """
    """
    if not isinstance(clientId, int):
        raise xmlrpc.client.Fault(-401, "Argument 'clientId' must be integer")
    #endif
    
    if clientId != 1001:
        return { "status" : 404, "statusMessage" : "Client not found" }
    #endif
 
    allowAttrs = ("name", "address", "city", "zipCode", "state", "phoneNo")
    
    for key in attr.keys():
        if key not in allowAttrs:
            raise xmlrpc.client.Fault(-401, "Argument '%s' is not allowed."\
                                      % key)
        #endif
        if not isinstance(attr[key], str):
              raise xmlrpc.client.Fault(-401, "Argument '%s' must be string."\
                                      % key)
        #endif
    #endfor
    
    return { "status" : 200, "statusMessage" : "OK" }
#enddef

    
def misc_listLanguages():
    """
    """
    return { "status" : 200, "statusMessage" : "OK", \
            "languages" : ["cz", "pl", "sk", "en"] }
#enddef
