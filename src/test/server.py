#!/usr/bin/python3
#-*- coding: utf-8 -*-

#import program
import group
import message

methodRegister = {
                  "chat.group.create" : (group.group_create, "S:s,S:sb"),
                  "chat.group.remove" : (group.group_remove, "S:i"),
                  "chat.group.enable" : (group.group_enable, "S:i"),
                  "chat.group.disable" : (group.group_disable, "S:i"),
                  "chat.group.getAttributes" : (group.group_getAttributes, "S:i"),
                  "chat.group.setAttributes" : (group.group_setAttributes, "S:is"),
                  "chat.listGroups" : (group.listGroups, "S:,S:S,S:Si,S:Sii,S:Siis,S:Siiss"),
                  "chat.group.addRecipient" : (group.group_addRecipient, "S:ii"),
                  "chat.group.removeRecipient" : (group.group_removeRecipient, "S:ii"),
                  "chat.group.listRecipients" : (group.group_listRecipients, "S:i,S:ii,S:iii"),
                  "chat.message.create" : (message.message_create, "S:Ss"),
                  "chat.listMessages" : (message.listMessages, "S:,S:S,S:Si,S:Sii,S:Siis,S:Siiss")}

#methodRegister = { "listClients" : (program.listClients, "S:,S:S,S:Si,S:Sii,S:SiiA"),
#                  "client.getAttributes" : program.client_getAttributes,
#                  "client.setAttributes" : program.client_setAttributes,
#                  "client.create" : program.client_create,
#                  "misc.listLanguages" : program.misc_listLanguages }
