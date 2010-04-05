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
import simplejson as json
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
    
    def _is_open_cart_for_customer(self,customer_id):
        KaraCos._Db.log.debug("BEGIN _is_open_cart_for_customer")
        assert isinstance(customer_id,basestring), "Parameter person must be String - repr = %s " % customer_id
        result = None
        carts = self.__get_open_cart_for_customer__(customer_id)
        assert carts.__len__() <= 1, "_is_open_cart_for_customer : More than one active Cart for person"
        if carts.__len__() == 1:
            result = True
        else:
            result = False
    
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
    def cancel_shopping_cart(self):
        """
        """
        #person = self.__domain__._get_person_data()
        cart = self.get_open_cart_for_user()
        cart['status'] = 'cancel'
        cart.save()
        return
        
    def _add_adr_form(self):
        user = self.__domain__._get_person_data()
        result = None
        form = {'title': _("Adresse"),
         'submit': _('Ajouter'),
         'fields': [{'name':'label', 'title':'Libelle','dataType': 'TEXT'},
                 {'name':'street-address', 'title':'street-address','dataType': 'TEXT','formType': 'textarea'},
                 {'name':'postal-code', 'title':'Code Postal','dataType': 'TEXT'},
                 {'name':'locality', 'title':'Ville','dataType': 'TEXT'},
                 {'name':'region', 'title':'Etat','dataType': 'TEXT'},
                 {'name':'country-name', 'title':'Pays','dataType': 'TEXT'},
                 {'name':'new-adr','title':'Ajouter une adresse','dataType': 'HIDDEN', 'value': 'Ajouter'},
                 ] }
        if 'adrs' in user:
            forms = []
            
            for adr in user['adrs'].keys() :
                adrform = {}
                adrform = {'title': _("Adresse %s" % adr),
                     'submit': _('Utiliser'),
                     'fields': [
                 {'name':'label', 'title':'Libelle','dataType': 'TEXT', 'value': adr},
                 {'name':'street-address', 'title':'street-address','dataType': 'TEXT','formType': 'textarea', 'value':user['adrs'][adr]['street-address']},
                 {'name':'postal-code', 'title':'Code Postal','dataType': 'TEXT', 'value':user['adrs'][adr]['postal-code']},
                 {'name':'locality', 'title':'Ville','dataType': 'TEXT', 'value':user['adrs'][adr]['locality']},
                 {'name':'region', 'title':'Etat','dataType': 'TEXT', 'value':user['adrs'][adr]['region']},
                 {'name':'country-name', 'title':'Pays','dataType': 'TEXT', 'value':user['adrs'][adr]['country-name']},
                 {'name':'use-adr','title':'Utiliser cette adresse de livraison','dataType': 'HIDDEN', 'value': 'Utiliser'},
                             ] }
                
                forms.append(adrform)
            forms.append(form)
            result = forms
        else:
            result = form
        return result
    
    
    def add_cart_adr(self,user,adr_type,kw):
        """
         Add an address to shopping Cart
         adr_type : shipping / billing
        """
        assert adr_type == 'shipping' or adr_type == 'billing'
        adr_type = '%s_adr' % adr_type
        label = kw['label']
        del kw['label']
        if 'new-adr' in kw:
            if 'adrs' in user:
                del kw['new-addr']
                user['adrs'][label] = kw
            else:
                user['adrs'] = {label:kw}
            user.save()
            return
        if 'use-adr' in kw:
            del kw['use-adr']
            user['adrs'][label] = kw
            cart = self.get_open_cart_for_user()
            cart[adr_type] = user['adrs'][label]
            user.save()
            cart.save()
            return
    
    @KaraCos._Db.isaction
    def add_cart_shipping(self,*args,**kw):
        user = self.__domain__._get_person_data()
        self.add_cart_adr(user,'shipping',kw)
                
    add_cart_shipping.get_form = _add_adr_form
    
    @KaraCos._Db.isaction
    def add_cart_billing(self,*args,**kw):
        user = self.__domain__._get_person_data()
        self.add_cart_adr(user,'billing',kw)
                
    add_cart_billing.get_form = _add_adr_form
    
    @KaraCos._Db.isaction
    def validate_cart(self,*args,**kwds):
        """
        
        """
        #assert cart_id in kw, "Parameter not found, cart_id"
        cart = None
        if 'cart_id' in cherrypy.session:
            cart = self.db[cherrypy.session['cart_id']]
        else:
            cart = self.get_open_cart_for_user()
            cherrypy.session['cart_id'] = cart.id
        if not self.__domain__.is_user_authenticated():
            raise KaraCos._Core.exception.WebAuthRequired("auth required","/%s?method=validate_cart"%self.get_relative_uri(),self.__domain__)
        user = self.__domain__.get_user_auth()
        if user.id != cart['customer_id']:
            assert 'anonymous.%s' % cherrypy.session._id == cart['customer_id'], "Cart verification failure"
            if self._is_open_cart_for_customer(user.id):
                self.cancel_shopping_cart()
            cart['customer_id'] = user.id
            cart.save()
        if 'shipping_adr' not in cart:
            raise KaraCos._Core.exception.DataRequired("Validate shipping","","/%s?method=validate_cart"%self.get_relative_uri(),self,self.add_cart_shipping)        
        if 'billing_adr' not in cart:
            raise KaraCos._Core.exception.DataRequired("Validate billing","","/%s?method=validate_cart"%self.get_relative_uri(),self,self.add_cart_billing)
        cart['validated'] = True
        cart.save()
        return cart
    
    
    def _set_services_form(self):
        result = None
        form = {'title': _("Service"),
         'submit': _('Ajouter'),
         'fields': [{'name':'svc_name', 'title':'Nom du service','dataType': 'TEXT'},
                 ] }
        if 'conf_services' in self:
            forms = []
            
            for svc_conf in self['conf_services'].keys() :
                confform = {}
                confform = {'title': _("Service %s" % svc_conf),
                     'submit': _('Utiliser'),
                     'fields': [
                             ] }
                
                forms.append(confform)
            forms.append(form)
            result = forms
        else:
            result = form
        return result
    
    @KaraCos._Db.isaction
    def set_services(self,*args,**kw):
        """
        """
        assert 'svc_name' in kw
        if 'conf_services' not in self:
            self['conf_services'] = { }
        if kw['svc_name'] not in self['conf_services']:
            self['conf_services'][kw['svc_name']] = {}
        self.save()
    
    set_services.get_form = _set_services_form
    
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
        

        
        