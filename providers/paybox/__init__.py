
import os
from subprocess import Popen, PIPE, STDOUT
import karacos

_default_conf = {
        "target_url": "https://preprod-tpeweb.paybox.com/cgi/MYchoix_pagepaiement.cgi",
        "PBX_SITE": "1999888",
        "PBX_RANG": "99",
        "PBX_IDENTIFIANT": "2",
        "PBX_OUTPUT": "D",
        "PBX_DEVISE": "978", #Code devise EURO     
    }

class Service(dict):
    __conf__ = {}
    def __init__(self,*args,**kw):
        self.log = karacos.core.log.getLogger(self)
        self.__conf__.update(_default_conf)
        self.__conf__["binary"] = os.path.join(karacos.apps['store'].__path__[0],'resources','bin','modulev3_unbuntu10_64bits.cgi_')
        self.log.debug("Service Paybox INIT values : %s,%s" % (args,kw))
        assert isinstance(args[0],dict)
        self.__conf__.update(args[0])
                             
        
    def update_conf(self,conf):
        self.__conf__.update(conf)
        
    def call(self, *args, **kw):
        assert 'params' in kw
        params = [self.__conf__["binary"], 'PBX_MODE=4']
        assert len(self.__conf__["PBX_SITE"]) == 7
        assert len(self.__conf__["PBX_RANG"]) == 2
        assert len(self.__conf__["PBX_OUTPUT"]) == 1
        assert len(self.__conf__["PBX_IDENTIFIANT"]) >= 1 and len(self.__conf__["PBX_IDENTIFIANT"]) <= 9
        assert len(kw['params']["PBX_IDENTIFIANT"]) >= 1 and len(kw['params']["PBX_IDENTIFIANT"]) <= 9
        assert  len(kw['params']['PBX_ANNULE']) <= 150
        assert  len(kw['params']['PBX_REFUSE']) <= 150
        assert  len(kw['params']['PBX_EFFECTUE']) <= 150
        assert  len(kw['params']['PBX_REPONDRE_A']) <= 150
        if 'PBX_OPT' in kw['params']:
            assert  len(kw['params']['PBX_OPT']) <= 150
        assert  len(kw['params']['PBX_BACKUP1']) <= 150
        assert  len(kw['params']['PBX_BACKUP2']) <= 150
        assert  len(kw['params']['PBX_BACKUP3']) <= 150
        assert  len(kw['params']['PBX_BACKUP3']) <= 150
        assert  len(kw['params']['PBX_PAYBOX']) <= 150
        assert  len(kw['params']['PBX_PORTEUR']) <= 80 and len(kw['params']['PBX_PORTEUR']) >= 6
        assert  len(kw['params']['PBX_RETOUR']) <= 150 and len(kw['params']['PBX_RETOUR']) >= 3
        assert  len(kw['params']['PBX_SOURCE']) <= 5 and len(kw['params']['PBX_SOURCE']) >= 3
        assert  len(kw['params']['PBX_TOTAL']) <= 10 and len(kw['params']['PBX_TOTAL']) >= 3
        assert  len(kw['params']['PBX_DEVISE']) == 3
        assert  len(kw['params']['PBX_CMD']) <= 250 and len(kw['params']['PBX_CMD']) >= 1
        
        params.append(str("PBX_SITE=%s" % self.__conf__["PBX_SITE"]))
        params.append(str("PBX_OUTPUT=D"))#%s" % self.__conf__["PBX_OUTPUT"])) # Should no be choosable
        params.append(str("PBX_RANG=%s" % self.__conf__["PBX_RANG"]))
        params.append(str("PBX_IDENTIFIANT=%s" % self.__conf__["PBX_IDENTIFIANT"]))
        for pkey in kw['params'].keys():
            params.append(str('%s="%s"' % (pkey, kw['params'][pkey])))
        cmd = ""
        for parambloc in params:
            cmd = cmd + ' ' + parambloc
        self.log.warn(params)
        call = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        call.wait()
        result = { "stdout": call.stdout.read(), "params": params, "retcode": call.returncode}
        self.log.warn(result)
        return result