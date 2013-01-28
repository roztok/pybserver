#!/usr/bin/python3
#-*- coding: utf-8 -*-

import xmlrpc.client
import psycopg2
from lib.config import config
from lib import validate
from lib import utils


def listMessages(filter={}, offset=0, limit=1000, criterion="id", direction="desc"):
    """
    Vypise seznam zprav vyhovujici filtru
    """
    where = "WHERE 1=1"
    
    validate.validateStruct(filter, "filter", ("groupId", "recipientId", 
                                               "senderId", "senderStationName",
                                               "dateCreate"))
    groupId = filter.get("groupId")
    if not groupId is None:
        validate.validateGroupId(groupId)
        where += " AND chatgroup_id=%s" % groupId
    #endif

    recipientId = filter.get("recipientId")
    if not recipientId is None:
        validate.validateRecipientId(recipientId)
        where += " AND recipient_id=%s" % recipientId
    #endif

    senderId = filter.get("senderId")
    if not senderId is None:
        if not isinstance(senderId, int):
            raise xmlrpc.client.Fault(-401, "Param 'senderId' must be int.")
        #endif
        where += " AND sender_id=%s" % senderId
    #endif

    senderStationName = filter.get("senderStationName")
    if not senderStationName is None:
        if not isinstance(senderStationName, str):
            raise xmlrpc.client.Fault(-401, \
                                       "Param 'senderStationName' must be string.")
        #endif
        if not senderStationName.strip():
            return {"status" : 401, 
                    "statusMessage" : "Param 'senderStationName' mustn't be empty."}
        #endif
        where += " AND senderStationName='%s'" % senderStationName
    #endif

    validate.validateOffset(offset)
    validate.validateLimit(limit)
    validate.validateCriterion(criterion, ("id", "dateCreate"))
    if criterion == "dateCreate":
        criterion = "date_create"
    #endif
    validate.validateDirection(direction)
    return {"status" : 200, "statusMessage" : "OK"}
    conn = config.sql.getDB()
    cur = conn.cursor()
    msgList = []
    try:
        cur.execute("""
                    SELECT 
                        id, sender_id, sender_name, sender_station_name,
                        chatgroup_id, recipient_id, recipient_name, date_create,
                        body
                    FROM message
                    %s
                    ORDER BY %s %s
                    OFFSET %s
                    LIMIT %s 
                    """ % (where, criterion, direction, offset, limit))
        
        for row in cur.fetchall():
            item = {"id" : row[0], 
                    "senderId" : utils.getNotNone(row[1], 0), 
                    "senderName" : utils.getNotNone(row[2], ""), 
                    "senderStationName" : utils.getNotNone(row[3], ""),
                    "dateCreate" : xmlrpc.client.DateTime(row[7]),
                    "body" : row[8]}
            if not row[4] is None:
                item["groupId"] = row[4]
            #endif
            if not row[5] is None:
                item["recipientId"] = row[5]
            #endif
            if not row[6] is None:
                item["recipientName"] = row[6]
            #endif
            msgList.append(item)
        #enfor

        cur.execute("""
                    SELECT count(*)
                    FROM message
                    %s 
                    """ % (where))
        resultSize = cur.fetchone()[0]
        conn.commit()
    except:
        conn.rollback()
        raise
    #endtry
    return {"status" : 200, "statusMessage" : "OK", 
            "messages" : msgList, "resultSize" : resultSize}
#enddef


def message_create(header, body):
    """
    Ulozi novou zpravu
    """
    #kontrola vstupu hlavicky - mozne parametry
    validate.validateStruct(header, "header", 
                            ("senderId", "senderName", "senderStationName",
                             "groupId", "recipientId", "recipientName"))
    #id odesilatele je povinne
    senderId = header.get("senderId")
    if not senderId:
        return {"status" : 401, "statusMessage" : "Missing 'senderId' in header."}
    #endif
    if not isinstance(senderId, int):
        raise xmlrpc.client.Fault(-401, "Param 'senderId' must be int.")
    #endif

    #nazev odesilatele je taktez povinny
    senderName = header.get("senderName")
    if not senderName:
        return {"status" : 401, "statusMessage" : "Missing 'senderName' in header."}
    #endif
    if not isinstance(senderName, str):
        raise xmlrpc.client.Fault(-401, "Param 'senderName' must be string.")
    #endif

    #nazev stanice odesilatele je nepovinne, pokud je zadane, nesmi byt prazdne
    senderStationName = header.get("senderStationName")
    if not senderStationName is None:
        if not isinstance(senderStationName, str):
            raise xmlrpc.client.Fault(-401, \
                                       "Param 'senderStationName' must be string.")
        #endif
        if not senderStationName.strip():
            return {"status" : 401, 
                    "statusMessage" : "Param 'senderStationName' mustn't be empty."}
        #endif
    #endif

    #id skuiny neni povinne, ale musi byt zadano jedno z id skupiny nebo id prijemce
    groupId = header.get("groupId")
    if not groupId is None:
        validate.validateGroupId(groupId)
    #endif

    recipientId = header.get("recipientId")
    if not recipientId is None:
        validate.validateRecipientId(recipientId)
    #endif

    recipientName = header.get("recipientName")
    if not recipientName is None:
        if not isinstance(recipientName, str):
            raise xmlrpc.client.Fault(-401, \
                                      "Param 'recipientName' must be string.")
        #endif
        if not recipientName.strip():
            return {"status" : 401, 
                    "statusMessage" : "Param 'recipientName' mustn't be empty."}
        #endif
    #endif

    #pokud je zadano id prijemce, zaroven pozaduji nazev prijemce
    elif recipientId:
        return {"status" : 401,
                "statusMessage" : "Missing 'recipientName' in header."}
    #endif

    #musi byt zadan prijemce nebo skupina
    if not recipientId and not groupId:
        return {"status" : 401,
                "statusMessage" : "Missing 'recipientId' or 'groupId' in header."}
    #endif

    if not isinstance(body, str):
        return xmlrpc.client.Fault(-401, "Argument 'body' must be string.")
    #endif


    conn = config.sql.getDB()
    cur = conn.cursor()
    try:
        cur.execute("""
                    INSERT INTO message
                        (sender_id, sender_name, sender_station_name, 
                        chatgroup_id, recipient_id, recipient_name, date_create,
                        body)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, NOW(), %s)
                    RETURNING id
                    """,  (senderId, senderName, senderStationName, groupId,
                           recipientId, recipientName, body))
        id = cur.fetchone()[0]
        conn.commit()
    except:
        conn.rollback()
        raise
    #endtry

    return  {"status" : 200, "statusMessage" : "OK", "messageId" : id}
#enddef