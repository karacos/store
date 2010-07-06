'''
Created on 13 janv. 2010

@author: nico
'''

import KaraCos

class Payment(KaraCos.Db.Node):
    '''
    Basic resource
    '''


    def __init__(self,parent=None,base=None,data=None):
        KaraCos.Db.Node.__init__(self,parent=parent,base=base,data=data)
        self.__cart__ = parent
        self.__store__ = parent.__store__
        #self._service = self.__store__._get_service(self['service'])

    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(parent,KaraCos.Db.ShoppingCart), "Parent type invalid : %s - Should be Store" % type(parent)
        assert 'service' in data
        assert data['service'] in parent.__store__._get_services()
        assert isinstance(data,dict)
        if 'type' not in data:
            data['type'] = 'Payment'
        result = KaraCos.Db.Node.create(parent=parent,base=base,data=data,owner=owner)
        return result

    @KaraCos._Db.isaction
    def do_forward(self):
        """
        Creates payment for service
        """
        return self.__store__._get_service(self['service']).do_forward(self.__cart__,self)
    
    @KaraCos._Db.isaction
    def do_callback(self,action,*args,**kw):
        """
        """
        self.log.info("do_callback : -- %s -- %s --" % (args,kw))
        result = self.__store__._get_service(self['service']['name']).do_callback(self,action,*args,**kw)
        
        return result

    def do_cancel(self):
        ""
        self['status'] = 'canceled'
        self.parent['is_open'] = 'false'
        self.__cart__['status'] = 'payment_ko'
        return "Operation Cancelled"
    
    def do_validate(self):
        ""
        self.__cart__['status'] = 'payment_ok'
        self.__cart__['valid_payment'] = self.id
        self.__cart__.save()
        return "Operation Validated"
        
        
        