'''
Created on 13 janv. 2010

@author: nico
'''

__author__="Nicolas Karageuzian"
__contributors__ = []

from uuid import uuid4
import sys
import cherrypy
import KaraCos
_ = KaraCos._
fields = KaraCos._Rpc.DynForm.fields

class Store(KaraCos.Db.StoreParent):
    '''
    Basic resource
    '''


    def __init__(self,parent=None,base=None,data=None):
        KaraCos.Db.StoreParent.__init__(self,parent=parent,base=base,data=data)
    
    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent.__domain__,KaraCos.Db.MDomain)
        if 'WebType' not in data:
            data['WebType'] = 'Store'
        return KaraCos.Db.WebNode.create(parent=parent,base=base,data=data,owner=owner)
    
    
    @KaraCos._Db.ViewsProcessor.isview('self','javascript')
    def __get_open_cart_for_customer__(self,customer_id):
        """
        function(doc) {
            if (doc.parent_id == "%s" && doc.customer_id == "%s" && doc.type == "ShoppingCart") {
                if (doc.status == "open")
                    emit(doc._id,doc._id)
                }
            }
        """
    
    def _get_open_cart_for_customer(self,customer_id):
        KaraCos._Db.log.debug("BEGIN _get_active_cart_for_customer")
        assert isinstance(customer_id,basestring), "Parameter person must be String - repr = %s " % customer_id
        result = None
        carts = self.__get_open_cart_for_customer__(customer_id)
        assert carts.__len__() <= 1, "_get_active_cart_for_customer : More than one active Cart for person"
        if carts.__len__() == 1:
            for cart in carts:
#                    KaraCos._Db.log.debug("get_child_by_name : db.key = %s db.value = %s" % (child.key,domain.value) )
                result = self.db[cart.key]
        else:
            name = "%s" % uuid4().hex
            data = {'name':name, 'status':'open', 'is_active': 'true', 'customer_id': customer_id}
            self._create_child_node(data=data,type="ShoppingCart")
            result = self.__childrens__[name]
    
        return result
    
    def get_open_cart_for_user(self):
        ""
        customer_id = ''
        if self.__domain__.is_user_authenticated():
            customer_id = self.__domain__.get_user_auth().id
        else:
            customer_id = 'anonymous.%s' % cherrypy.session._id
        return self._get_open_cart_for_customer(customer_id)
            
        
        
    
    @KaraCos._Db.isaction
    def view_shopping_cart(self):
        """
        """
        #person = self.__domain__._get_person_data()
        return self.get_open_cart_for_user()
    
    @KaraCos._Db.isaction
    def _get_services(self):
        """
        """
        assert 'conf_services' in self
        return self['conf_services'].keys()
    
    def _get_service_config(self,service):
        """
        """
        assert 'conf_services' in self
        assert service in self['conf_services']
        return self['conf_services'][service]
    
    def _get_service(self,service):
        if '__services__' not in dir(self):
            self.__services__ = dict()
        if service not in self.__services__:
            assert service in self._get_services()
            svc_cls = KaraCos.Apps['store'].services.get_service(service)
            self.__services__[service] = svc_cls((self._get_service_config(service)))
        return self.__services__[service]
    
    @KaraCos._Db.isaction
    def pay_cart(self,*args,**kw):
        """
        """
        assert 'service' in kw
        service = kw['service']
        assert service in self._get_services()
        person = self.__domain__._get_person_data()
        cart = self.get_open_cart_for_user()
        
        payment = cart._create_payment(self._get_service(service))
        return payment.do_forward()
        
    
    @KaraCos._Db.isaction
    def validate_cart(self):
        """
        Check for valid user, create user if required
        """
        
    @KaraCos.expose
    def pay_callback(self,*args,**kwds):
        """
        url handler for payment services callback
        """
        arg_list,kw = args
        payment_id,action = arg_list
        self.log.info("pay_callback : -- %s -- %s --" % (payment_id,action))
        user = self.__domain__._get_person_data()
        cart = self._get_process_pay_cart_for_payment(payment)
        payment = cart.get_child_by_id(payment_id)
        self.log.info("pay_callback : -- %s --" % (payment))
        result = payment.do_callback(action,*(),**kw)
        template = self.__domain__.lookup.get_template('/default/system')
        return template.render(instance=self,result=result)
        

        
        