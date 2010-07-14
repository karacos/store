'''
Created on 5 mars 2010

@author: nico
'''

import cherrypy
import KaraCos

class Service(KaraCos.Apps['store'].providers.paypal.Service):
    
    def __init__(self,*args,**kw):
        """
        """
        KaraCos.Apps['store'].providers.paypal.Service.__init__(self,*args,**kw)
        self['_name'] = 'paypal_express'
        
    
    def do_forward(self,cart,payment):
        assert isinstance(cart, KaraCos.Db.ShoppingCart)
        assert isinstance(payment, KaraCos.Db.Payment)
        payment['service'] = {'name':self['_name']}
        bill = cart._get_bill_data()
        kw = {'amt': "%.2f" % bill['net_total'],
              'ITEMAMT':"%.2f" % bill['net_total'],
              'returnurl':"http://%s%s/pay_callback/%s/return" % (cart.__store__.__domain__['fqdn'],
                                                                   cart.__store__._get_action_url(),
                                                                   payment.id),
              'cancelurl':"http://%s%s/pay_callback/%s/cancel" % (cart.__store__.__domain__['fqdn'],
                                                                   cart.__store__._get_action_url(),
                                                                   payment.id),
              'CURRENCYCODE': 'EUR',
              'PAYMENTACTION': 'Sale',
              #'TAXAMT': "%.2f" % bill['tax_total']
              }
        i = 0
        for  item  in bill['items'].values():
            ""
            kw['L_NAME%s' %i ] = item['name']
            kw['L_AMT%s' %i ] = "%.2f" % item['net_total']
            #kw['L_QTY%s' %i ] = "%.2f" % item['number']
            #kw['L_TAXAMT%s' %i ] = "%.2f" % (item['tax'] * item['price'] + item['price'])
            
            i+=1
            
        payment['service']['SetExpressCheckout'] = {'request':kw}
        response = self.call('SetExpressCheckout', **kw)
        KaraCos._Db.log.info("Service PAYPAL response : %s" % response.raw)
        payment['service']['SetExpressCheckout']['response'] = response.raw
        payment.save()
        if payment['service']['SetExpressCheckout']['response']['ACK'][0] == "Failure":
            raise cherrypy.HTTPRedirect('/', 301)
        redirect_url = "%s%s&AMT=%s&CURRENCYCODE=EUR" % (self.__conf__['PAYPAL_URL'],
                                 payment['service']['SetExpressCheckout']['response']['TOKEN'][0],
                                 "%.2f" % bill['net_total'])
        raise cherrypy.HTTPRedirect(redirect_url, 301)

        
        
    def do_callback(self,payment,action,*args,**kw):
        """
        """
        kw = {'TOKEN': payment['service']['SetExpressCheckout']['response']['TOKEN'][0]
              }
        payment['service']['GetExpressCheckoutDetails'] = {'request': kw}
        response = self.call('GetExpressCheckoutDetails', **kw)
        payment['service']['GetExpressCheckoutDetails']['response'] = response.raw
        payment.save()
        
        if action == 'cancel':
            return payment.do_cancel()
        if action == 'return':
            kw = {'TOKEN': payment['service']['SetExpressCheckout']['response']['TOKEN'][0],
                  'PAYERID':payment['service']['GetExpressCheckoutDetails']['response']['PAYERID'][0],
                  'AMT':payment['service']['GetExpressCheckoutDetails']['response']['AMT'][0],
                  'CURRENCYCODE':'EUR',
                  'PAYMENTACTION':'Sale'
                  }
            payment['service']['DoExpressCheckoutPayment'] = {'request': kw}
            response = self.call('DoExpressCheckoutPayment', **kw)
            payment['service']['DoExpressCheckoutPayment']['response'] = response.raw
            payment.save()
            return payment.do_validate()