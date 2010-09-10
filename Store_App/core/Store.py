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
        if 'stylesheets' not in self:
            self['stylesheets'] = []
        if 'store' not in self['stylesheets']:
            self['stylesheets'].append("store")
    
    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent.__domain__,KaraCos.Db.MDomain)
        if 'WebType' not in data:
            data['WebType'] = 'Store'
        return KaraCos.Db.WebNode.create(parent=parent,base=base,data=data,owner=owner)

    @KaraCos._Db.isaction
    def create_bo_node(self, type='StoreBackOffice'):
        assert issubclass(KaraCos.Db.__dict__[type], KaraCos.Db.StoreBackOffice), _("Type is not StoreBackOffice subclass")
        data = {'name':'_backoffice'}
        self._create_child_node(data=data, type=type, base=True)
    create_bo_node.form = {'title':'Creates BackOffice Node',
                           'submit': 'Create',
                           'fields': [{'name': 'type', 'title':'Type','dataType': 'TEXT','value':'StoreBackOffice'}]}
    def _get_backoffice_node(self):
        if '_backoffice' not in self['childrens']:
            raise KaraCos._Core.exception.DataRequired("please create backoffice node", _("Create BO node"),"/%s/"%self.get_relative_uri(),self,self.create_bo_node)
        return self.db[self['childrens']['_backoffice']]

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
    def _publish_node(self):
        KaraCos.Db.WebNode._publish_node(self)
        self['ACL']['group.everyone@%s' % self.__domain__['name']].append("add_cart_billing")
        self['ACL']['group.everyone@%s' % self.__domain__['name']].append("add_cart_shipping")
        self['ACL']['group.everyone@%s' % self.__domain__['name']].append("cancel_shopping_cart")
        self['ACL']['group.everyone@%s' % self.__domain__['name']].append("pay_cart")
        self['ACL']['group.everyone@%s' % self.__domain__['name']].append("validate_cart")
        self['ACL']['group.everyone@%s' % self.__domain__['name']].append("view_shopping_cart")
        self['ACL']['group.everyone@%s' % self.__domain__['name']].append("remove_item_from_cart")
        self['ACL']['group.everyone@%s' % self.__domain__['name']].append("set_number_item")
        self.save()
        
    @KaraCos._Db.isaction
    def publish_node(self):
        self._publish_node()
        return {'status':'success', 'message':_("L'Artiste est maintenant visible de tous")}
    
    def _get_open_cart_for_customer(self,customer_id):
        KaraCos._Db.log.debug("BEGIN _get_open_cart_for_customer")
        assert isinstance(customer_id,basestring), "Parameter person must be String - repr = %s " % customer_id
        result = None
        carts = self.__get_open_cart_for_customer__(customer_id)
        assert carts.__len__() <= 1, "_get_open_cart_for_customer : More than one active Cart for person"
        if carts.__len__() == 1:
            for cart in carts:
#                    KaraCos._Db.log.debug("get_child_by_name : db.key = %s db.value = %s" % (child.key,domain.value) )
                result = self.db[cart.key]
        else:
            name = "%s" % uuid4().hex
            data = {'name':name, 'status':'open',
                    'is_active': 'true', 'customer_id': customer_id}
            self._create_child_node(data=data,type="ShoppingCart")
            result = self.__childrens__[name]
    
        return result
    
    def _get_open_carts_for_customer(self,customer_id):
        self.log.debug("BEGIN _get_open_carts_for_customer")
        assert isinstance(customer_id,basestring), "Parameter person must be String - repr = %s " % customer_id
        result = []
        carts = self.__get_open_cart_for_customer__(customer_id)
        for cart in carts:
            result.append(self.db[cart.key])
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
        user = self.__domain__.get_user_auth()
        cart = None
        customer_id = ''
        if self.__domain__.is_user_authenticated():
            customer_id = user.id
        else:
            customer_id = 'anonymous.%s' % cherrypy.session._id
        if 'cart_id' in cherrypy.session:
            cart = self.db[cherrypy.session['cart_id']]
            if user.id != cart['customer_id']:
                if cart['customer_id'] == 'anonymous.%s' % cherrypy.session._id:
                    cart['customer_id'] = customer_id
                    cart.save()
                else:
                    del cherrypy.session['cart_id']
                    cart = None
        if cart == None:    
            cart = self._get_open_cart_for_customer(customer_id)
        cherrypy.session['cart_id'] = cart.id
        return cart
    
    def get_open_carts_for_user(self):
        """
        Same as above, but returns an array of shoppingcarts and don't fails if more than one (useful for user to trac and remove his old commands)
        """
        user = self.__domain__.get_user_auth()
        customer_id = ''
        if self.__domain__.is_user_authenticated():
            customer_id = user.id
        else:
            assert False, _("Unavailable to anonymous user")
            
        result = self._get_open_carts_for_customer(customer_id)
        return result
        
    @KaraCos._Db.isaction
    def view_shopping_cart(self):
        """
        """
        #person = self.__domain__._get_person_data()
        return {'status':'success','data':self.get_open_cart_for_user(),'datatype':'ShoppingCart'}

    @KaraCos._Db.isaction
    def remove_item_from_cart(self,item_id=None):
        """
        """
        cart = self.get_open_cart_for_user()
        if item_id in cart['items']:
            del cart['items'][item_id]
            cart.save()
            return {'status' :'success', 'message':_("item retire du panier avec succes")}
        else:
            return {'status' :'failure', 'message': _("'l'item ne fait pas partie du panier")}
            
    @KaraCos._Db.isaction
    def set_number_item(self,item_id=None,number=None):
        """
        sets a new number of given items in shopping Cart
        """
        cart = self.get_open_cart_for_user()
        if item_id in cart['items']:
            cart['items'][item_id] = int(number)
            cart.save()
            return {'status' :'success', 'message':_("item modifie avec succes")}
        else:
            return {'status' :'failure', 'message': _("'l'item ne fait pas partie du panier")}
        
    
    @KaraCos._Db.isaction
    def cancel_shopping_cart(self):
        """
        """
        #person = self.__domain__._get_person_data()
        cart = self.get_open_cart_for_user()
        cart['status'] = 'cancel'
        cart.save()
        return
        
    def _add_shipping_adr_form(self):
        user = self.__domain__._get_person_data()
        result = None
        form = {'title': _("Adresse"),
         'submit': _('Ajouter'),
         'notice': _("Nouvelle adresse de livraison"),
         'fields': [{'name':'label', 'title':'Libelle','dataType': 'TEXT'},
                 {'name':'destname', 'title':_('Nom du destinataire'),'dataType': 'TEXT'},
                 {'name':'street-address', 'title':'street-address','dataType': 'TEXT','formType': 'TEXTAREA'},
                 {'name':'postal-code', 'title':'Code Postal','dataType': 'TEXT'},
                 {'name':'locality', 'title':'Ville','dataType': 'TEXT'},
                 {'name':'region', 'title':'Etat','dataType': 'TEXT'},
                 {'name':'country-name', 'title':'Pays','dataType': 'TEXT'},
                 {'name':'new-adr','dataType': 'HIDDEN', 'value': 'Ajouter'},
                 ] }
        if 'adrs' in user:
            forms = []
            adrform = {'title': _("Adresse de livraison"),
                       'submit': _('Utiliser'),
                       'notice': _("Choisissez une adresse pour la livraison"),
                       'fields': [{'name':'use-adr','dataType': 'HIDDEN', 'value': 'Utiliser'}] }
            adrsfield = {'name':'label', 'title':'Choisissez une adresse','dataType': 'TEXT', 'formType':'RADIO', 'values': []}
            for adr in user['adrs'].keys() :
                fieldlabel = "%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s" % (adr,
                                     user['adrs'][adr]['destname'],
                                     user['adrs'][adr]['street-address'],
                                     user['adrs'][adr]['postal-code'],
                                     user['adrs'][adr]['locality'],
                                     user['adrs'][adr]['region'],
                                     user['adrs'][adr]['country-name'])
                adrsfield['values'].append({'value':adr,'label':fieldlabel})
                
            adrform['fields'].append(adrsfield)
            forms.append(adrform)
            forms.append(form)
            result = forms
        else:
            result = form
        return result
    
    
    def _add_billing_adr_form(self):
        user = self.__domain__._get_person_data()
        result = None
        form = {'title': _("Adresse"),
         'submit': _('Ajouter'),
         'notice': _("Nouvelle adresse de facturation"),
         'fields': [{'name':'label', 'title':'Libelle','dataType': 'TEXT'},
                    {'name':'destname', 'title':_('Nom du destinataire'),'dataType': 'TEXT'},
                 {'name':'street-address', 'title':'street-address','dataType': 'TEXT','formType': 'TEXTAREA'},
                 {'name':'postal-code', 'title':'Code Postal','dataType': 'TEXT'},
                 {'name':'locality', 'title':'Ville','dataType': 'TEXT'},
                 {'name':'region', 'title':'Etat','dataType': 'TEXT'},
                 {'name':'country-name', 'title':'Pays','dataType': 'TEXT'},
                 {'name':'new-adr','dataType': 'HIDDEN', 'value': 'Ajouter'},
                 ] }
        if 'adrs' in user:
            forms = []
            adrform = {'title': _("Adresse de facturation"),
                       'submit': _('Utiliser'),
                       'notice': _("Choisissez une adresse pour la facturation"),
                       'fields': [{'name':'use-adr','dataType': 'HIDDEN', 'value': 'Utiliser'}] }
            adrsfield = {'name':'label', 'title':'Choisissez une adresse','dataType': 'TEXT', 'formType':'RADIO', 'values': []}
            for adr in user['adrs'].keys() :
                if 'destname' not in user['adrs'][adr]:
                    user['adrs'][adr]['destname'] = ""
                fieldlabel = "%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s" % (adr,
                                     user['adrs'][adr]['destname'],
                                     user['adrs'][adr]['street-address'],
                                     user['adrs'][adr]['postal-code'],
                                     user['adrs'][adr]['locality'],
                                     user['adrs'][adr]['region'],
                                     user['adrs'][adr]['country-name'])
                adrsfield['values'].append({'value':adr,'label':fieldlabel})
                
            adrform['fields'].append(adrsfield)
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
            cart = self.get_open_cart_for_user()
            cart[adr_type] = user['adrs'][label]
            user.save()
            cart.save()
            return
    
    @KaraCos._Db.isaction
    def add_cart_shipping(self,*args,**kw):
        user = self.__domain__._get_person_data()
        self.add_cart_adr(user,'shipping',kw)
                
    add_cart_shipping.get_form = _add_shipping_adr_form
    add_cart_shipping.label = _("Adresse de livraison")
    
    @KaraCos._Db.isaction
    def add_cart_billing(self,*args,**kw):
        user = self.__domain__._get_person_data()
        self.add_cart_adr(user,'billing',kw)
                
    add_cart_billing.get_form = _add_billing_adr_form
    add_cart_billing.label = _("Adresse de Facturation")
    
    @KaraCos._Db.isaction
    def validate_cart(self,*args,**kwds):
        """
        
        """
        self.log.info("START validate_cart")
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
        cart._do_self_validation()
        self._get_backoffice_node()._validate_cart(cart)
        return {'status':'success','data':cart,'datatype':'ShoppingCart'}
    
    
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
                     'submit': _('Modifier'),
                     'fields': [{'name':'svc_name', 'title':'Nom du service','dataType': 'HIDDEN','value':svc_conf},
                             ] }
                if svc_conf == 'paypal_express':
                    self.set_paypal_express_conf()
                    self.set_paypal_express_form(confform)
                forms.append(confform)
            forms.append(form)
            result = forms
        else:
            result = form
        return result
    
    def set_paypal_express_form(self,form):
        for key in self['conf_services']['paypal_express'].keys():
            field = {'name' : key,
                     'title': key,
                    'value' : self['conf_services']['paypal_express'][key],
                    'dataType': 'TEXT'
                     }
            form['fields'].append(field)
        
    def set_paypal_express_conf(self):
        default = KaraCos.Apps['store'].providers.paypal._default_conf
        for key in default.keys():
            if key not in self['conf_services']['paypal_express']:
                self['conf_services']['paypal_express'][key] = default[key]
        self.save()
        
        
    @KaraCos._Db.isaction
    def set_services(self,*args,**kw):
        """
        """
        assert 'svc_name' in kw
        assert kw['svc_name'] in ['paypal_express'], "Incorrect service Name"
        svc_name = kw['svc_name']
        del kw['svc_name']
        if 'conf_services' not in self:
            self['conf_services'] = {svc_name: kw }
        else :
            self['conf_services'][svc_name] = kw
        
        self.save()
    
    set_services.get_form = _set_services_form
    
    def __get_services__(self):
        """
        """
        assert 'conf_services' in self
        return self['conf_services'].keys()
    
    @KaraCos._Db.isaction
    def _get_services(self):
        """
        """
        return {'status':'success','message':self.__get_services__()}
    
    def _get_service_config(self,service):
        """
        """
        assert 'conf_services' in self
        assert service in self['conf_services']
        return self['conf_services'][service]
    
    def _get_service(self,service):
        self.log.info("_get_service : -- %s --" % (service))
        if '__services__' not in dir(self):
            self.__services__ = dict()
        if service not in self.__services__:
            assert service in self.__get_services__()
            svc_cls = KaraCos.Apps['store'].services.get_service(service)
            self.__services__[service] = svc_cls((self._get_service_config(service)))
        return self.__services__[service]
    
    @KaraCos._Db.isaction
    def pay_cart(self,*args,**kw):
        """
        """
        assert 'service' in kw
        service = kw['service']
        assert service in self.__get_services__()
        person = self.__domain__._get_person_data()
        cart = self.get_open_cart_for_user()
        payment = cart._create_payment(self._get_service(service))
        return payment.do_forward()
    
    
    @KaraCos.expose
    def pay_callback(self,*args,**kwds):
        """
        url handler for payment services callback
        """
        #arg_list,kw = args
        payment_id,action = args
        self.log.info("pay_callback : -- %s -- %s --" % (payment_id,action))
        user = self.__domain__._get_person_data()
        cart = self.get_open_cart_for_user()
        self.log.info("pay_callback CART : -- %s --" % (cart))
        payment = cart.get_child_by_id(str(payment_id))
        self.log.info("pay_callback ID/PAYMENT : -- %s -- %s --" % (payment_id,payment))
        result = payment.do_callback(action,*(),**kwds)
        template = self.__domain__.lookup.get_template('/default/system')
        return template.render(instance=self,result=result)
        

        
        