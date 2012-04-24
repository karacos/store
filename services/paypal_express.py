'''
Created on 5 mars 2010

@author: nico
'''


import karacos

class Service(karacos.apps['store'].providers.paypal.Service):
    
    def __init__(self,*args,**kw):
        """
        """
        self.log = karacos.core.log.getLogger(self)
        karacos.apps['store'].providers.paypal.Service.__init__(self,*args,**kw)
        self['_name'] = 'paypal_express'
        
    
    def do_forward(self,cart,payment):
        assert isinstance(cart, karacos.db['ShoppingCart'])
        assert isinstance(payment, karacos.db['Payment'])
        payment['service'] = {'name':self['_name']}
        bill = cart._get_bill_data()
        kw = {'AMT': bill['total'],
              'CURRENCYCODE': 'EUR',
              'PAYMENTREQUEST_0_AMT':  bill['total'],
              'PAYMENTREQUEST_0_CURRENCYCODE': 'EUR',
              'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
              'INVNUM':  payment.id,
              #'PAYMENTREQUEST_0_SHIPPINGAMT': bill['shipping'],
              'RETURNURL':"http://%s%s/pay_callback/%s/return" % (cart.__store__.__domain__['fqdn'],
                                                                   cart.__store__._get_action_url(),
                                                                   payment.id),
              'CANCELURL':"http://%s%s/pay_callback/%s/cancel" % (cart.__store__.__domain__['fqdn'],
                                                                   cart.__store__._get_action_url(),
                                                                   payment.id)
              
              }
        """,
              'PAYMENTREQUEST_0_ITEMAMT': bill['net_total'],
              'PAYMENTREQUEST_0_INVNUM': payment['_id'],
              'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
              'PAYMENTREQUEST_0_TAXAMT': bill['tax_total'],
              'PAYMENTREQUEST_0_TRANSACTIONID': payment.id,
              ]
              }
        i = 0
        for  item  in bill['items'].values():
            ""
            kw['L_PAYMENTREQUEST_0_NAME%s' %i ] = item['name']
            kw['L_PAYMENTREQUEST_0_DESC%s' %i ] = item['title']
            kw['L_PAYMENTREQUEST_0_AMT%s' %i ] =  item['total'] # item['price'] #
            kw['L_L_PAYMENTREQUEST_0_QTY%s' %i ] = item['number']
            kw['L_PAYMENTREQUEST_0_TAXAMT%s' %i ] = item['tax_amt']
            
            i+=1
        """
            
        payment['service']['SetExpressCheckout'] = {'request':kw}
        payment.save()
        response = self.call('SetExpressCheckout', **kw)
        self.log.info("Service PAYPAL response : %s" % response.raw)
        payment['service']['SetExpressCheckout']['response'] = response.raw
        payment.save()
        if payment['service']['SetExpressCheckout']['response']['ACK'][0] == "Failure":
            return {'success': False, 'data': { "id": payment.id,
                                               "response": payment['service']['SetExpressCheckout']['response']}}
        redirect_url = "%s%s&PAYMENTREQUEST_0_AMT=%s&PAYMENTREQUEST_0_CURRENCYCODE=EUR" % (self.__conf__['PAYPAL_URL'],
                                 payment['service']['SetExpressCheckout']['response']['TOKEN'][0],
                                  bill['total'])
        return {'success': True, 'data' :{"id": payment.id,"service": "paypal_express",'url': redirect_url}}

        
        
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
                  'PAYMENTREQUEST_0_AMT':payment['service']['GetExpressCheckoutDetails']['response']['AMT'][0],
                  'PAYMENTACTION':'Sale',
                  'CURRENCYCODE': payment['service']['GetExpressCheckoutDetails']['response']['CURRENCYCODE'][0],
                  }
            """
                  'PAYMENTREQUEST_0_ITEMAMT':payment['service']['SetExpressCheckout']['request']['PAYMENTREQUEST_0_ITEMAMT'],
                  'PAYMENTREQUEST_0_TAXAMT':payment['service']['SetExpressCheckout']['request']['PAYMENTREQUEST_0_TAXAMT'],
                  'PAYMENTREQUEST_0_CURRENCYCODE':'EUR',
                  'PAYMENTREQUEST_0_SHIPPINGAMT':payment['service']['SetExpressCheckout']['request']['PAYMENTREQUEST_0_SHIPPINGAMT'],
            """
            if 'DoExpressCheckoutPayment' not in payment['service']:
                payment['service']['DoExpressCheckoutPayment'] = {'request': kw}
                response = self.call('DoExpressCheckoutPayment', **kw)
                payment['service']['DoExpressCheckoutPayment']['response'] = response.raw
                payment.save()
                
            if payment['service']['DoExpressCheckoutPayment']['response']['ACK'][0] == "Failure":
                return {'success': False, 
                        'datatype': 'payment_validation',
                        'data': { "id": payment.id,
                            "response": payment['service']['DoExpressCheckoutPayment']['response']}}
            return payment.do_validate()