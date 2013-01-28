#!/usr/bin/python3
#-*- coding: utf-8 -*-

import xmlrpc.client
import psycopg2
from lib.config import config
from lib import validate


def group_create(name, active = xmlrpc.client.Boolean(True)):
    """
    Vytvori novou skupinu s name pripadne nastavi zda je aktivni ci nikolov
    """
    #kontrola vstupu
    validate.validateGroupName(name)
    validate.validateBoolean(active, "active")
    
    conn = config.sql.getDB() 
    cur = conn.cursor()
    try:
        cur.execute("""INSERT INTO 
                            chatgroup 
                            VALUES (DEFAULT,'%s', %s)
                            RETURNING id"""
                            % (name, active))
        id = cur.fetchone()[0]
        conn.commit()
    except:
        conn.rollback()
        raise
    #endtry

    return {"status" : 200, "statusMessage" : "OK", "groupId" : id}
#enddef


def group_remove(groupId):
    """
    Odstrani skupinu, pokud v ni nejsou zadni prijemci.
    """
    #kontrola vstupu
    validate.validateGroupId(groupId)
    #endif

    conn = config.sql.getDB()
    cur = conn.cursor()
    try:
        cur.execute("""
                    DELETE FROM chatgroup WHERE id = %s
                    """ % groupId)
        conn.commit()
        if not cur.rowcount:
            return {"status" : 404, 
                    "statusMessage" : "Group with id='%s' not found." % groupId}
        #endif
    except psycopg2.IntegrityError:
        conn.rollback()
        return {"status" : 403, 
                "statusMessage" : "Group with id '%s' is not empty." % groupId}
    except:
        conn.rollback()
        raise
    #endtry

    return {"status" : 200, "statusMessage" : "OK"}
#enddef


def group_enable(groupId):
    return _group_enable_disable(groupId, True)
#enddef


def group_disable(groupId):
    return _group_enable_disable(groupId, False)
#enddef


def _group_enable_disable(groupId, active = True):
    """
    Aktivuje /deaktivuje skupinu
    """
    validate.validateGroupId(groupId)

    conn = config.sql.getDB()
    cur = conn.cursor()
    try:
        cur.execute("""
                    SELECT active 
                    FROM chatgroup 
                    WHERE id = %s""" % groupId)
        
        if not cur.fetchone():
            conn.rollback()
            return {"status" : 404, 
                    "statusMessage" : "Group with id='%s' not found." % groupId}
        #endif
        
        cur.execute("""
                    UPDATE chatgroup SET active = %s WHERE id = '%s'
                    """ % (active, groupId))    
        conn.commit()
    except:
        conn.rollback()
        raise
    #endtry

    return {"status" : 200, "statusMessage" : "OK"}
#enddef


def group_getAttributes(groupId):
    """
    Vraci atributy skupiny
    """
    validate.validateGroupId(groupId)
    
    conn = config.sql.getDB()
    cur = conn.cursor()
    try:
        cur.execute("""
                    SELECT 
                        id, name, active 
                    FROM chatgroup 
                    WHERE id = %s""" % groupId)
        conn.commit()
    except:
        conn.rollback()
        raise
    #endtry

    attr = cur.fetchone()
    return { "status" : 200, "statusMessage" : "OK", 
            "groupAttributes" : { "id" : attr[0], "name" : attr[1], 
                                "active" : xmlrpc.client.Boolean(attr[2])
                                }}
#enddef


def group_setAttributes(groupId, name):
    """
    Nastavuje atributy skupiny
    """
    validate.validateGroupId(groupId)
    validate.validateGroupName(name)
    
    conn = config.sql.getDB()
    cur = conn.cursor()
    try:
        cur.execute("""
                    SELECT active 
                    FROM chatgroup 
                    WHERE id = %s""" % groupId)
        
        if not cur.fetchone():
            conn.rollback()
            return {"status" : 404, 
                    "statusMessage" : "Group with id='%s' not found." % groupId}
        #endif
        
        cur.execute("""
                    UPDATE chatgroup SET name = '%s' WHERE id = '%s'
                    """ % (name, groupId))    
        conn.commit()
    except:
        conn.rollback()
        raise
    #endtry

    return {"status" : 200, "statusMessage" : "OK"}
#enddef


def listGroups(filter={}, offset=0, limit=1000, criterion="id", direction="asc"):
    """
    Vypis seznamu skupin
    """
    validate.validateStruct(filter, "filter", ("active",))
    active = filter.get("active", None)
    if active:
        validate.validateBoolean(active, "filter:active")
    #endif

    validate.validateOffset(offset)
    validate.validateLimit(limit)
    validate.validateCriterion(criterion, ("name","id","active"))
    validate.validateDirection(direction)
    
    groups = ( {
            "active" : True,
            "id"    : 1,
            "name"  : "test1"
        },
            {
            "active" : True,
            "id"    : 1,
            "name"  : "test1"
        },
        {
            "active" : True,
            "id"    : 1,
            "name"  : "test1"
        },
            {
            "active" : True,
            "id"    : 1,
            "name"  : "test1"
        },
        {
            "active" : True,
            "id"    : 1,
            "name"  : "test1"
        },
            {
            "active" : True,
            "id"    : 1,
            "name"  : "test1"
        }
        ,{
            "active" : True,
            "id"    : 1,
            "name"  : "test1"
        },
            {
            "active" : True,
            "id"    : 1,
            "name"  : "test1"
        }
    )

    return {"status" : 200, "statusMessage" : "OK", 
            "groups" : groups, "resultSize" : resultSize}
    conn = config.sql.getDB()
    cur = conn.cursor()
    groupList = []
    try:
        if active:
            where = "WHERE active = True"
        else:
            where = ""
            
        cur.execute("""
                    SELECT id, name, active
                    FROM chatgroup
                    %s
                    ORDER BY %s %s
                    OFFSET %s
                    LIMIT %s 
                    """ % (where, criterion, direction, offset, limit))
        
        for row in cur.fetchall():
            groupList.append({"id" : row[0], "name" : row[1], 
                            "active" : xmlrpc.client.Boolean(row[2])})
        #enfor
        #celkovy pocet skupin
        cur.execute("""
                    SELECT count(*)
                    FROM chatgroup
                    %s 
                    """ % (where))
        resultSize = cur.fetchone()[0]
        conn.commit()
    except:
        conn.rollback()
        raise
    #endtry

    return {"status" : 200, "statusMessage" : "OK", 
            "groups" : groupList, "resultSize" : resultSize}
#endef


def group_addRecipient(groupId, recipientId):
    """
    Prida prijemce do skupiny
    """
    validate.validateGroupId(groupId)
    validate.validateRecipientId(recipientId)

    conn = config.sql.getDB()
    cur = conn.cursor()

    try:
        cur.execute("""
                    INSERT INTO  
                        chatgroup_recipient (chatgroup_id, recipient_id)
                    VALUES (%s, %s)
                    """ % (groupId, recipientId))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()

        #check if record already exist
        cur.execute("""
                    SELECT count(*) FROM 
                        chatgroup_recipient
                    WHERE
                        chatgroup_id = %s
                        AND
                        recipient_id = %s
                    """ % (groupId, recipientId))
        conn.commit()
        if cur.fetchone():
            return {"status" : 201, 
                    "statusMessage" : "Recipient '%s' allready in "\
                    "group '%s'." % (groupId, recipientId)}
        #endif

        return {"status" : 404, 
                "statusMessage" : "Group with id '%s' doesn't exist." % groupId}
    except:
        conn.rollback()
        raise
    #endtry

    return {"status" : 200, "statusMessage" : "OK"}
#enddef


def group_removeRecipient(groupId, recipientId):
    """
    Odebere prijemce ze skupiny
    """
    validate.validateGroupId(groupId)
    validate.validateRecipientId(recipientId)

    conn = config.sql.getDB()
    cur = conn.cursor()

    try:
        cur.execute("""
                    SELECT id 
                    FROM chatgroup 
                    WHERE id = %s""" % groupId)
        
        if not cur.fetchone():
            conn.rollback()
            return {"status" : 404, 
                    "statusMessage" : "Group with id='%s' not found." % groupId}
        #endif

        cur.execute("""
                    DELETE FROM 
                        chatgroup_recipient
                    WHERE
                        chatgroup_id = %s
                        AND
                        recipient_id = %s
                    """ % (groupId, recipientId))
        conn.commit()
        if not cur.rowcount:
            return {"status" : 201, 
                    "statusMessage" : "Recipient '%s' not in group '%s'." % 
                    (recipientId, groupId)}
        #endif
    except:
        conn.rollback()
        raise
    #endtry

    return {"status" : 200, "statusMessage" : "OK"}
#enndef


def group_listRecipients(groupId, offset=0, limit=1000):
    """
    Vypis seznamu prijemcu ze skupiny
    """
    validate.validateGroupId(groupId)
    validate.validateOffset(offset)
    validate.validateLimit(limit)
    
    conn = config.sql.getDB()
    cur = conn.cursor()
    groupList = []
    try:
        
        cur.execute("""
                    SELECT id
                    FROM chatgroup
                    WHERE id = %s 
                    """ % groupId)
        if not cur.fetchone():
            conn.rollback()
            return {"status" : 404, 
                    "statusMessage" : "Group with id='%s' not found." % groupId}
        #endif
        
        cur.execute("""
                    SELECT recipient_id
                    FROM chatgroup_recipient
                    WHERE chatgroup_id = %s
                    ORDER BY recipient_id ASC
                    OFFSET %s
                    LIMIT %s 
                    """ % (groupId, offset, limit))

        list = []
        for row in cur.fetchall():
            list.append(row[0])
        #endfor
        #celkovy pocet prijemcu ve skupine
        cur.execute("""
                    SELECT count(*)
                    FROM chatgroup_recipient
                    WHERE chatgroup_id = %s
                    """ % (groupId))
        resultSize = cur.fetchone()[0]
        conn.commit()
    except:
        conn.rollback()
        raise
    #endtry

    return {"status" : 200, "statusMessage" : "OK", 
            "recipients" : list,
            "resultSize" : resultSize}
#endef
