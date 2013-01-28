#!/usr/bin/python3
#-*- coding: utf-8 -*-

"""
Easy xmlrpc server
"""

import sys
import signal
import getopt
import time
import os
import configparser
import logging
import multiprocessing

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpc.client

import pidfile



"""
Drzi konfiguraci serveru
Konfiguracni soubor je klasicky text/plain 'ini' soubor
@see http://en.wikipedia.org/wiki/INI_file
""" 
class RPCServerConfig:


    def __init__(self):
        """
        Konstruktor
        parsuje konfiguraci pomoci configparseru
        @param configfile cesta ke konfiguracnimu souboru
        """
        
        #spusteni z comandline
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'hc:', [])
        except getopt.GetoptError:
            print("Bad arguments by script calling")
            printHelp()
            sys.exit(2)
        
        confFile = ""
        #naplni parametry
        for opt, arg in opts:
            if opt == "-h":
                printHelp()
                sys.exit()
            #elif opt == '-d':
            #debug = True
            elif opt == '-c':
                confFile = arg
            #endif
        #endfor
        if not confFile or not os.path.isfile(confFile):
            print("Missing config file '%s'.\nExiting..." % confFile)
            sys.exit()
        #endif
        
        self.configFile = confFile
        self.parser = configparser.ConfigParser()
        self.parser.read(self.configFile)

        #ziskani konfigurace serveru
        self.server = _ServerConfig(self.parser)

    #enddef


    def getConfig(self):
        """
        Vraci rozparsovanou konfiguraci
        """
        return self.parser
    #enddef
#endclass


"""
Drzi systemove nastaveni serveru
"""
class _ServerConfig:

    def __init__(self, parser):
        """
        Rozparsuje sekci [server], kde se nachazi systemove nastaveni serveru
        """
        self.pidFile = parser.get("server", "PidFile")
        self.logFile = parser.get("server", "LogFile")
        self.helpFile = parser.get("server", "HelpFile")
        self.startWorkers = parser.getint("server", "StartWorkers")
        self.hostname = parser.get("server", "Hostname")
        self.port = int(parser.get("server", "Port"))
        self.modulePath = parser.get("server", "ModulePath")
    #enddef
#endclass


"""
Pretizeny SimpleXMLRPCServer pro zapnuti allow_reuse_address na True
budeme to pouzivat ve forku
Zaroven logovani reguestu a podpora dokumentace
pozor, zalezi na jaky "hostname" resp. sitove rozhrani se pripojujeme
napr. localhost jde pouze z localhost
"""
class RPCServer(SimpleXMLRPCServer):
    allow_reuse_address = True

    def __init__(self, serverConfig):
        self.config = serverConfig
        SimpleXMLRPCServer.__init__(self, (self.config.server.hostname, \
                self.config.server.port))
        
        self.logger = logging.getLogger("xmlrpcserver::%s:%s" % (\
                self.config.server.hostname, self.config.server.port))
        self.logger.setLevel(logging.INFO)
        
        lh = logging.StreamHandler()
        lh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s::%(name)s::%(message)s')
        lh.setFormatter(formatter)
        self.logger.addHandler(lh)
        
        self.methodHelpList = {}
        self.methodSignatureList = {}
        self._parserHelpFile()
    #enddef


    def _registerSignature(self, method, signature):
        """
        Registrace signatury metody. Jednotlive signatury se oddeluji carkou
        Tabulka signatur:
        +------------------+
        | A | array        |
        +------------------+
        | S | struct       |
        +------------------+
        | B | binary       |
        +------------------+
        | D | datetime     |
        +------------------+
        | b | boolean      |
        +------------------+
        | d | double       |
        +------------------+
        | i | int          |
        +------------------+
        | s | string       |
        +------------------+
        """
        self.methodSignatureList[method] = signature
    #enddef


    def _parserHelpFile(self):
        """
        Parsovani help dokumentu
        """
        try:
            file = open(self.config.server.helpFile, "r")
        except IOError as err:
            self.logger.warning("Reading help file error. %s '%s'" % \
                                (err.strerror, err.filename))
            return False
        #endtry
            
        buff = ""
        while (1):
            line = file.readline()
            if not line:
                break
            #endif
            buff = buff + line
            if line == ".\n":
                self.methodHelpList[buff.split("\n")[0]] = buff
                buff = ""
            #endif
        #endwhile
        
        return True
    #enddef


    def _dispatch(self, method, params):
        #st = time.time()
        try:
            func = None
            try:
                # check to see if a matching function has been registered
                func = self.funcs[method]
            except KeyError:
                if self.instance is not None:
                    # check for a _dispatch method
                    if hasattr(self.instance, '_dispatch'):
                        return self.instance._dispatch(method, params)
                    else:
                        # call instance method directly
                        try:
                            func = resolve_dotted_attribute(
                                self.instance,
                                method,
                                self.allow_dotted_names
                                )
                        except AttributeError:
                            pass
                        #endtry
                    #endif
                #endif
            #endtry 
    
            if func is not None:
                self.msg = None
                startTime = time.time()
                res = {"status":500, "statusMessage":"Internal server error"}
                try:
                    res = func(*params)
                except xmlrpc.client.Fault as fault:
                    self.msg = "FAULT=%s" % fault
                    raise fault
                except Exception as e:
                    raise
                finally:
                    endTime = time.time()
                    spentTime = (endTime-startTime)*1000
                    if not self.msg:
                        if method.split(".")[0] == "system":
                            self.msg = "SYSTEM MESSAGE CALL"
                        else:
                            self.msg = "STATUS=%s:MESSAGE='%s'" % (res["status"], \
                                                          res["statusMessage"])
                        #endif
                    #endif
                    self.logger.info("%s::%.4fms::%s%s" % (self.msg, spentTime, \
                                                              method, params))
                #endtry
                #self.logger.info(">>>>>>%s<<<<" % ((time.time()-st)*1000))
                return res
            else:
                raise xmlrpc.client.Fault(-404, 'method "%s" is not supported' % method)
            #endif
        except xmlrpc.client.Fault:
            raise
        except Exception as e:
            import traceback
            self.logger.error(traceback.print_exc())              
            res = {"status" : 500, "statusMessage" : "%s" % e}
            return res
        #endtry
    #enddef


    def system_methodHelp(self, methodName):
        """
        Pretizime poskytovani dokumentace rozhrani
        """
        return self.methodHelpList.get(methodName, \
                                           "Method help not available.")
    #enddef


    def system_methodSignature(self, methodName):
        """
        Pretizime poskytovani informaci o signature metody
        +------------------+
        | A | array        |
        +------------------+
        | S | struct       |
        +------------------+
        | B | binary       |
        +------------------+
        | D | datetime     |
        +------------------+
        | b | boolean      |
        +------------------+
        | d | double       |
        +------------------+
        | i | int          |
        +------------------+
        | s | string       |
        +------------------+
        """
        signatureMap = {"A" : "array",
                        "S" : "struct", 
                        "B" : "binary",
                        "D" : "datetime",
                        "b" : "boolean",
                        "d" : "double",
                        "i" : "int",
                        "s" : "string"}
        try:
            signature = self.methodSignatureList[methodName].split(",")
        except KeyError:
            return "Method signature not available"
        #endtry

        output = ""
        for sig in signature:
            (out, params) = sig.split(":")
            
            paramString = ""
            for param in params:
                if not param:
                    break
                #endif
                #print(param)
                paramString += "%s, " % signatureMap[param]
            #endfr 
            if paramString:
                paramString = paramString[:-2]
            #endif
            
            output += "%s %s(%s)\n" % (signatureMap[out], methodName, paramString)
        #endfor
        return output
    #enddef


    def runChildserver(self):
        """
        Pro child process zapneme smycku
        """
        try:
            self.serve_forever()
        finally:
            self.server_close()
        #endtry
    #enddef
#endclass


def childProcess(RPCServer, signalHandler):
    """
    Spoustec pro podproces
    """
    #registrujeme puvodni SIGTERM handler
    signal.signal(signal.SIGTERM, signalHandler)
    RPCServer.runChildserver()
#enddef


class ProcessDispatcher:
    """
    Process dispatcher
    ridi procesy, kontroluje a vytvari nove, zarazuje je do poolu
    po ukonceni programu ukoncuje vsechny potomky
    """
    
    def __init__(self, startWorkers, RPCServer, signalHandler):
        """
        """
        #seznam podprocesu
        self.pool = {}
        #pocet podprocesu
        self.startWorkers = startWorkers
        #instance rpcserveru
        self._rpcserver = RPCServer
        #signal handler - pro deticky se pouziva nativni
        #pro master process vlastni viz. dispatcher
        self._signalHandler = signalHandler
        self.logger = logging.getLogger("dispatcher")
        self.logger.setLevel(logging.DEBUG)
        
        lh = logging.StreamHandler()
        lh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s::%(name)s::%(levelname)s::%(message)s')
        lh.setFormatter(formatter)
        self.logger.addHandler(lh)
    #enddef
    
    
    def __call__(self, a, b):
        """
        Pretizeni pro ukonceni workeru po odchyceni signalu
        """
        self._cleaner()
    #enddef


    def checkWorkers(self):
        """
        Kontroluje podprocesy, vytvari nove
        """
        #kontrola, zda procesy bezi
        for pid in tuple(self.pool.keys()):
            self.logger.debug("Checking process '%s'.", pid)
            
            if not self.pool[pid].is_alive():
                self.logger.info("Process with PID '%s' killed.", pid)
                #self.pool[pid].terminate()
                del self.pool[pid]
            #endif
        #endfor
        
        #pokud bezi vsechny procesy, je vse v poradku a zde koncime
        if len(self.pool) == self.startWorkers:
            self.logger.debug("All process ('%s') are running.", self.startWorkers)
            return
        #endif

        #vytvoreni procesu
        while (len(self.pool) < self.startWorkers):
            process = multiprocessing.Process(target=childProcess, \
                        args=(self._rpcserver, self._signalHandler))
            process.start()
            self._addProcess(process)
        #endwhile
    #enddef


    def _addProcess(self, process):
        """
        Prida process do poolu
        """
        self.logger.info("New process with PID='%s' started.", process.pid)
        self.pool[process.pid] = process
    #enddef;


    def _cleaner(self):
        """
        Postrili podprocesy, ukonci server
        """
        for pid in tuple(self.pool.keys()):
            #self.pool[pid].terminate()
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                if self.pool[pid].is_alive:
                    self.pool[pid].terminate
            finally:
                self.logger.info("SIGTERM: child with PID='%s' terminated.", pid)
                del self.pool[pid]
            #endtry
        #endfor
        self.logger.info("Server is going down...")
        sys.exit()
    #enddef
#endclass


def printHelp():
    print("rpcserver \n  -c <config file>")
#enddef


def main():
    
    #nacteni konfigurace
    rpcserverConfig = RPCServerConfig()
    
    #import modulu
    #prida cestu k modulum pro include
    sys.path.append(os.getcwd())
    sys.path.append(rpcserverConfig.server.modulePath)

    if not os.path.isfile("%s/server.py" % \
        rpcserverConfig.server.modulePath):
        
        print("Missing server module in path: '%s'\nExiting..." % \
            rpcserverConfig.server.modulePath)
        sys.exit()
    #endif
    
    #vytvori pidFile - fork save 1, zapise pid az po forku
    #pidFile = pidfile.PidFile(rpcserverConfig.server.pidFile, 0)
    
    #import modulu server s mapovanim method rozhrani
    import server
    
    #spusteni xmlrpcserveru
    rpcserver = RPCServer(rpcserverConfig)
    rpcserver.register_introspection_functions()

    #registrace method rozhrani
    try:
        for name in server.methodRegister:
            # log print(name)
            try:
                rpcserver.register_function(server.methodRegister[name][0], name)
            except TypeError:
                rpcserver.register_function(server.methodRegister[name], name)
            try:
                rpcserver._registerSignature(name, server.methodRegister[name][1])
            except TypeError:
                pass
            #endtry
            
        #endfor
    except AttributeError:
        print("Missing method register...")
        sys.exit()
    #endtry

    signalHandler = signal.getsignal(signal.SIGTERM)
    dispatcher = ProcessDispatcher(rpcserverConfig.server.startWorkers, \
                    rpcserver, signalHandler)
    
    signal.signal(signal.SIGTERM, dispatcher)
    
    # main loop
    while 1:
        dispatcher.checkWorkers()
        time.sleep(2)
    #endwhile
    
#enddef


if __name__ == "__main__":
    main()
    