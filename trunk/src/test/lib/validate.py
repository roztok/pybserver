#!/usr/bin/python3
#-*- coding: utf-8 -*-

import xmlrpc.client


def validateStruct(struct, structName, supportedKeys=()):
    """
    Kontroluje strrukturu podle typu a zaroven zda je prislusny klic podporovan
    """
    if not isinstance(struct, dict):
        raise xmlrpc.client.Fault(-401, "Argument '%s'" \
                                  " must be struct." % structName)
    #endif

    for key in struct:
        if not key in supportedKeys:
            raise  xmlrpc.client.Fault(401, "Key '%s' in argument '%s'" \
                                  " is not suppoorted." % (key, structName))
        #endif
    #endfor
#enddef


def validateBoolean(bool, boolName):
    """
    """
    if not isinstance(bool, xmlrpc.client.Boolean):
        raise xmlrpc.client.Fault(-401, "Argument '%s'" \
                                  " must be xmlrpc-boolean." % boolName)
    #endif
#enddef


def validateOffset(offset):
    """
    Kontroluje offset pro vypis seznamu
    """
    if not isinstance(offset, int):
        raise xmlrpc.client.Fault(-401, "Argument 'offset'" \
                                  " must be int.")
    #endif

    if offset < 0:
        raise xmlrpc.client.Fault(401, "Argument 'offset'" \
                                  " must be greater or equal zero.")
    #endif
#enddef


def validateLimit(limit):
    """
    Kontroluje limit pro vypis seznamu
    """
    if not isinstance(limit, int):
        raise xmlrpc.client.Fault(-401, "Argument 'limit'" \
                                  " must be int.")
    #endif

    if limit < 0:
        raise xmlrpc.client.Fault(401, "Argument 'limit'" \
                                  " must be greater or equal zero.")
    #endif
#enddef


def validateDirection(direction):
    """
    Kontroluje smer trideni vypisu ASC, DESC
    """
    if not isinstance(direction, str):
        raise xmlrpc.client.Fault(-401, "Argument 'direction'" \
                                  " must be string.")
    #endif

    if not direction.lower() in ("asc", "desc"):
        raise xmlrpc.client.Fault(401, "Argument 'direction'" \
                                  " must be one from 'desc', 'asc' but" \
                                  " '%s' given." % direction)
    #endif
#enddef


def validateCriterion(criterion, supportedCriterion):
    """
    Kontroluje parametr trideni vypisu
    """
    if not isinstance(criterion, str):
        raise xmlrpc.client.Fault(-401, "Argument 'criterion'" \
                                  " must be string.")
    #endif

    if not criterion in supportedCriterion:
        raise xmlrpc.client.Fault(401, "Argument 'criterion'" \
                                  " must be one from '%s' but" \
                                  " '%s' given." % (supportedCriterion, 
                                                    criterion))
    #endif
#enddef


def validateGroupId(groupId):
    """
    Kontroluje id skupiny
    """
    if not isinstance(groupId, int):
        raise xmlrpc.client.Fault(-401, "Argument 'groupId'" \
                                  " must be int.")
    #endif
#enddef


def validateRecipientId(recipientId):
    """
    Kontroluje id prijemce
    """
    if not isinstance(recipientId, int):
        raise xmlrpc.client.Fault(-401, "Argument 'recipientId'" \
                                  " must be int.")
    #endif
#enddef


def validateGroupName(name):
    """
    Kontroluje nazev skupiny
    """
    if not isinstance(name, str):
        raise xmlrpc.client.Fault(-401, "Argument 'name'" \
                                  " must be string.")
    #endif
#enddef
