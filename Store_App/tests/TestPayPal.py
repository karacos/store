'''
Created on 17 juin 2010

'''
__author__ = "Nicolas Karageuzian"
__contributors__ = []
from cherrypy.test import webtest
import simplejson as json
import unittest
import urllib
import KaraCos
import sys

class TestPayPalExpress(webtest.WebCase):
    conf = {
                'API_ENDPOINT': "https://api-3t.sandbox.paypal.com/nvp",
                'API_AUTHENTICATION_MODE': "3TOKEN",

                # 3TOKEN credentials
                'API_USERNAME': "tzs_1267712030_biz_api1.traderzic.com",
                'API_PASSWORD': "1267712034",
                'API_SIGNATURE': "AH8QxOKmWbAdt4LBjWJRhWwATMUtAiqSnIlSwmTS9O9piLWVsJ7r7kDs",
                # TODO: implement use of API via http proxy
                'USE_PROXY': True,
                'PROXY_HOST': "127.0.0.1",
                'PROXY_PORT': "8888",
                # in seconds
                'HTTP_TIMEOUT': 15,
                'PAYPAL_URL': "https://www.sandbox.paypal.com/webscr?cmd=_express-checkout&token=",
                'VERSION': "60.0",
                'ACK_SUCCESS': "SUCCESS",
                'ACK_SUCCESS_WITH_WARNING': "SUCCESSWITHWARNING",
                'API_AUTHENTICATION_MODES': ("3TOKEN", "UNIPAY"),
            }
    def test_call(self):
        svc_cls = KaraCos.Apps['store'].services.get_service("paypal_express")
        service = svc_cls(self.conf)
        kw = {'amt': "%.2f" % 22,
              'ITEMAMT':"%.2f" % 22,
              'returnurl':"http://%s%spay_callback/%s/return",
              'cancelurl':"http://%s%spay_callback/%s/cancel",
              'CURRENCYCODE': 'EUR',
              'PAYMENTACTION': 'Sale',
              #'TAXAMT': "%.2f" % bill['tax_total']
              'L_NAME1': "item",
              'L_AMT1': "%.2f" % 22
              }
        service.call('SetExpressCheckout', **kw)



class TestSuite(unittest.TestSuite):
        pass

payPalTestSuite = TestSuite()

payPalTestSuite.addTest(TestPayPalExpress("test_call"))

KaraCos.Tests.suites.append(payPalTestSuite)