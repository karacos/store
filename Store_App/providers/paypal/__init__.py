'''
Created on 5 mars 2010

@author: nico
'''
from cgi import parse_qs
import socket
import urllib
import urllib2
from urlparse import urlsplit, urlunsplit

import KaraCos

_default_conf = {
                'API_ENDPOINT': "https://api-3t.sandbox.paypal.com/nvp",
                'API_AUTHENTICATION_MODE': "3TOKEN",

                # 3TOKEN credentials
                'API_USERNAME': "tzs_1267712030_biz_api1.traderzic.com",
                'API_PASSWORD': "1267712034",
                'API_SIGNATURE': "AH8QxOKmWbAdt4LBjWJRhWwATMUtAiqSnIlSwmTS9O9piLWVsJ7r7kDs",
                # TODO: implement use of API via http proxy
                'USE_PROXY': False,
                'PROXY_HOST': "127.0.0.1",
                'PROXY_PORT': "8080",
                # in seconds
                'HTTP_TIMEOUT': 15,
                'PAYPAL_URL': "https://www.sandbox.paypal.com/webscr?cmd=_express-checkout&token=",
                'VERSION': "60.0",
                'ACK_SUCCESS': "SUCCESS",
                'ACK_SUCCESS_WITH_WARNING': "SUCCESSWITHWARNING",
                'API_AUTHENTICATION_MODES': ("3TOKEN", "UNIPAY"),
            }

class Response(object):
    def __init__(self, query_string,conf):
        self.raw = parse_qs(query_string)
        self.__conf__ = conf

    def __str__(self):
        return str(self.raw)

    def __getattr__(self, key):
        key = key.upper()
        try:
            value = self.raw[key]
            if len(value) == 1:
                return value[0]
            return value
        except KeyError:
            raise AttributeError(self)

    def success(self):
        return self.ack.upper() in (self.__conf__['ACK_SUCCESS'], self.__conf__['ACK_SUCCESS_WITH_WARNING'])
    success = property(success)

class ApiError(Exception):
    pass

class Service(dict):
    __conf__ = {}
    def __init__(self,*args,**kw):
        """
        """
        self.__conf__.update(_default_conf)
        KaraCos._Db.log.debug("Service Paypal express INIT values : %s,%s" % (args,kw))
        assert isinstance(args[0],dict)
        self.__conf__.update(args[0])
                             
        
    
    
    def call(self,method, **kwargs):
        """
        Wrapper method for executing all API commands over HTTP. This method is
        further used to implement wrapper methods listed here:
    
        https://www.x.com/docs/DOC-1374
    
        ``method`` must be a supported NVP method listed at the above address.
    
        ``kwargs`` will be a hash of
        """
        http_timeout = 15
        try:
            http_timeout = float(self.__conf__['HTTP_TIMEOUT'])
        except:
            pass
        self.__conf__['HTTP_TIMEOUT'] = http_timeout    
        socket.setdefaulttimeout(http_timeout)
    
        urlvalues = {
            'METHOD': method,
            'VERSION': self.__conf__['VERSION']
        }
    
        if self.__conf__['API_AUTHENTICATION_MODE'] not in self.__conf__['API_AUTHENTICATION_MODES']:
            raise ApiError("Not a supported auth mode. Use one of: %s" % \
                           ", ".join(self.__conf__['API_AUTHENTICATION_MODES']))
        headers = {}
        if(self.__conf__['API_AUTHENTICATION_MODE'] == "3TOKEN"):
            # headers['X-PAYPAL-SECURITY-USERID'] = self.__conf__['API_USERNAME']
            # headers['X-PAYPAL-SECURITY-PASSWORD'] = self.__conf__['API_PASSWORD']
            # headers['X-PAYPAL-SECURITY-SIGNATURE'] = self.__conf__['API_SIGNATURE']
            urlvalues['USER'] = self.__conf__['API_USERNAME']
            urlvalues['PWD'] = self.__conf__['API_PASSWORD']
            urlvalues['SIGNATURE'] = self.__conf__['API_SIGNATURE']
        elif(self.__conf__['API_AUTHENTICATION_MODE'] == "UNIPAY"):
            # headers['X-PAYPAL-SECURITY-SUBJECT'] = SUBJECT
            urlvalues['SUBJECT'] = self.__conf__['SUBJECT']
        # headers['X-PAYPAL-REQUEST-DATA-FORMAT'] = 'NV'
        # headers['X-PAYPAL-RESPONSE-DATA-FORMAT'] = 'NV'
        # print(headers)
        for k,v in kwargs.iteritems():
            urlvalues[k.upper()] = v

        data = urllib.urlencode(urlvalues)
        req = urllib2.Request(self.__conf__['API_ENDPOINT'], data, headers)

        if self.__conf__["USE_PROXY"] == True or  self.__conf__["USE_PROXY"] == "True" or  self.__conf__["USE_PROXY"] == "true":
            #proxy_support = urllib2.ProxyHandler({"http" : "http://ahad-haam:3128"})
            req.set_proxy("%s:%s" %(self.__conf__['PROXY_HOST'],self.__conf__['PROXY_PORT']), 'https')
        response = Response(urllib2.urlopen(req).read(),self.__conf__)
    
        if not response.success:
            raise ApiError(response)
        return response
    
        