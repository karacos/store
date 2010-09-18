'''
Created on 13 janv. 2010

@author: nico
'''

import karacos

class Payment(karacos.db['Node']):
    '''
    Basic resource
    '''


    def __init__(self,parent=None,base=None,data=None):
        karacos.db['Node'].__init__(self,parent=parent,base=base,data=data)
        self.__cart__ = parent
        self.__store__ = parent.__store__
        #self._service = self.__store__._get_service(self['service'])

    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(parent,karacos.db['ShoppingCart']), "Parent type invalid : %s - Should be Store" % type(parent)
        assert 'service' in data
        assert 'name' in data['service']
        assert data['service']['name'] in parent.__store__.__get_services__()
        assert isinstance(data,dict)
        if 'type' not in data:
            data['type'] = 'Payment'
        result = karacos.db['Node'].create(parent=parent,base=False,data=data)
        return result

    def do_forward(self):
        """
        Creates payment for service
        """
        return self.__store__._get_service(self['service']['name']).do_forward(self.__cart__,self)
    
    def do_callback(self,action,*args,**kw):
        """
        """
        self.log.info("do_callback : -- %s -- %s --" % (args,kw))
        result = self.__store__._get_service(self['service']['name']).do_callback(self,action,*args,**kw)
        
        return result

    def do_cancel(self):
        ""
        self['status'] = 'canceled'
        self.save()
        self.__cart__._do_payment_cancelled(self)
        return "Operation Cancelled"
    
    def do_validate(self):
        "When payment is validated, service impl must calls do_validate()"
        self['status'] = 'validated'
        self.save()
        self.__cart__._do_payment_validated(self)
        return {'status':'success', 'message':"Operation Validated"}
        
        
        