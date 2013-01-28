#!/usr/bin/python3
#-*- coding: utf-8 -*-

def getNotNone(param, default=""):
    """
    Pokud je param None, vraci default
    """
    if param is None:
        return default
    else:
        return param
    #endif
#enddef


def xmlrpcDateTimeToDateTime(xmlrpcDateTime):
    """
    """
    xmlrpcDateTime.split("-")