'''
Created on 13 janv. 2010

@author: nico
'''
from uuid import uuid4
import sys
import KaraCos
_ = KaraCos._
fields = KaraCos._Rpc.DynForm.fields

class Store(KaraCos.Db.WebNode):
    '''
    Basic resource
    '''


    def __init__(self,parent=None,base=None,data=None):
        KaraCos.Db.WebNode.__init__(self,parent=parent,base=base,data=data)
    
    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent.__domain__,KaraCos.Db.MDomain)
        if 'WebType' not in data:
            data['WebType'] = 'Store'
        return KaraCos.Db.WebNode.create(parent=parent,base=base,data=data,owner=owner)
    
    
    @KaraCos._Db.ViewsProcessor.isview('self','javascript')
    def __get_active_cart_for_person__(self,person_id):
        """
        function(doc) {
            if (doc.parent_id == "%s" && doc.person_id == "%s" && doc.type == "ShoppingCart") {
                if (doc.is_open == "true")
                    emit(doc._id,doc._id)
                }
            }
        """
    
    def _get_active_cart_for_person(self,person):
        KaraCos._Db.log.debug("BEGIN _get_active_cart_for_person ")
        assert isinstance(person,KaraCos.Db.Person), "Parameter person must be Person"
        result = None
        carts = self.__get_active_cart_for_person__(person.id)
        assert carts.__len__() <= 1, "_get_active_cart_for_person : More than one active Cart for person"
        if carts.__len__() == 1:
            for cart in carts:
#                    KaraCos._Db.log.debug("get_child_by_name : db.key = %s db.value = %s" % (child.key,domain.value) )
                result = self.db[cart.key]
        else:
            name = "%s" % uuid4().hex
            data = {'name':name, 'is_open': 'true', 'person_id': person.id}
            self._create_child_node(data=data,type="ShoppingCart")
            result = self.__childrens__[name]
    
        return result
    
    @KaraCos._Db.isaction
    def view_shopping_cart(self):
        """
        """
        person = self.__domain__._get_person_data()
        return self._get_active_cart_for_person(person)
    
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
    def pay(self,*args,**kw):
        """
        """
        assert 'service' in kw
        service = kw['service']
        assert service in self._get_services()
        person = self.__domain__._get_person_data()
        cart = self._get_active_cart_for_person(person)
        payment = cart._create_payment(self._get_service(service))
        return payment.do_forward()
        
        
    @KaraCos.expose
    def pay_callback(self,*args,**kwds):
        """
        """
        arg_list,kw = args
        payment_id,action = arg_list
        self.log.info("pay_callback : -- %s -- %s --" % (payment_id,action))
        person = self.__domain__._get_person_data()
        cart = self._get_active_cart_for_person(person)
        payment = cart.get_child_by_id(payment_id)
        self.log.info("pay_callback : -- %s --" % (payment))
        result = payment.do_callback(action,*(),**kw)
        template = self.__domain__.lookup.get_template('/default/system')
        return template.render(instance=self,result=result)
        
    @KaraCos._Db.isaction
    def create_storeitem(self,*args,**kw):
        assert 'price' in kw
        kw['price'] = float(kw['price'])
        assert 'tax' in kw
        kw['tax'] = float(kw['tax'])
        assert 'shipping' in kw
        kw['shipping'] = float(kw['shipping'])
        self._create_child_node(data=kw,type='StoreItem')
    
    create_storeitem.form = {'title': _("Creer un produit"),
         'submit': _('Creer'),
         'fields': [{'name':'name', 'title':'Reference','dataType': 'TEXT'},
                 {'name':'description', 'title':'Description','dataType': 'TEXT', 'formType': 'textarea'},
                 {'name':'price', 'title':'Prix Hors Taxes','dataType': 'TEXT'},
                 {'name':'tax', 'title':'Valeur de taxe','dataType': 'TEXT'},
                 {'name':'shipping', 'title':'Frais de port','dataType': 'TEXT'},
                 ] }
        
        