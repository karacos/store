'''
Created on 13 janv. 2010

@author: nico
'''
import traceback

__author__="Nicolas Karageuzian"
__contributors__ = []

from uuid import uuid4
import os, sys
import karacos

class Store(karacos.db['StoreParent']):
    '''
    Basic resource
    '''


    def __init__(self,parent=None,base=None,data=None):
        if 'service' not in dir(karacos.apps['store']):
            karacos.apps['store'].services = __import__("services", karacos.apps['store'].__store_globals__, karacos.apps['store'].__store_locals__, ['all'], -1)
        karacos.db['StoreParent'].__init__(self,parent=parent,base=base,data=data)
        
        if 'stylesheets' not in self:
            self['stylesheets'] = []
        if 'store' not in self['stylesheets']:
            self['stylesheets'].append("store")
        staticdirname = os.path.join(karacos.apps['store'].__path__[0],'resources','static')
        self.__domain__['staticdirs']['_store'] = staticdirname
        store_templatesdir = os.path.join(karacos.apps['store'].__path__[0],'resources','templates')
        if 'templatesdirs' not in self.__domain__:
            self.__domain__['templatesdirs'] = [store_templatesdir]
        if store_templatesdir not in self.__domain__['templatesdirs']:
            self.__domain__['templatesdirs'].append(store_templatesdir)
        self.__domain__.save()
        self.__domain__.init_lookup()
    
    @staticmethod
    def create(parent=None, base=None,data=None):
        assert isinstance(data,dict)
        assert isinstance(parent.__domain__,karacos.db['MDomain'])
        if 'WebType' not in data:
            data['WebType'] = 'Store'
        return karacos.db['WebNode'].create(parent=parent,base=base,data=data)

    def _get_customers_group(self):
        self._update_item()
        if '__customers_group__' not in dir(self):
            name = 'customers@%s' % self.__domain__['name']
            if name not in self.__domain__._get_groups_node().__childrens__:
                self.__customers_group__ = self.__domain__._create_group(name, False)
            else:
                self.__customers_group__ = self.__domain__._get_groups_node().__childrens__[name]
        return self.__customers_group__ 

    @karacos._db.isaction
    def add_cart_customer_email(self, email):
        cart = self.get_open_cart_for_user()
        return cart.set_customer_email(email)

    @karacos._db.isaction
    def create_bo_node(self, type='StoreBackOffice'):
        assert issubclass(karacos.db[type], karacos.db['StoreBackOffice']), _("Type is not StoreBackOffice subclass")
        data = {'name':'_backoffice'}
        self._create_child_node(data=data, type=type, base=True)
    create_bo_node.form = {'title':'Creates BackOffice Node',
                           'submit': 'Create',
                           'fields': [{'name': 'type', 'title':'Type','dataType': 'TEXT','value':'StoreBackOffice'}]}

    def _get_backoffice_node(self):
        if '_backoffice' not in self['childrens']:
            raise karacos.http.DataRequired(self,self.create_bo_node,
                                            message=_("please create backoffice node"),
                                            backlink="/%s/"%self.get_relative_uri())
        return self.db[self['childrens']['_backoffice']]

    @karacos._db.ViewsProcessor.isview('self','javascript')
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
        karacos.db['StoreParent']._publish_node(self)
        if 'cancel_shopping_cart' not in self['ACL']['group.everyone@%s' % self.__domain__['name']]:
            self['ACL']['group.everyone@%s' % self.__domain__['name']].append("cancel_shopping_cart")
        if 'cancel_shopping_cart' not in self['ACL']['group.everyone@%s' % self.__domain__['name']]:
            self['ACL']['group.everyone@%s' % self.__domain__['name']].append("cancel_shopping_cart")
        if 'validate_cart' not in self['ACL']['group.everyone@%s' % self.__domain__['name']]:
            self['ACL']['group.everyone@%s' % self.__domain__['name']].append("validate_cart")
        if 'view_shopping_cart' not in self['ACL']['group.everyone@%s' % self.__domain__['name']]:
            self['ACL']['group.everyone@%s' % self.__domain__['name']].append("view_shopping_cart")
        if 'remove_item_from_cart' not in self['ACL']['group.everyone@%s' % self.__domain__['name']]:
            self['ACL']['group.everyone@%s' % self.__domain__['name']].append("remove_item_from_cart")
        if 'set_number_item' not in self['ACL']['group.everyone@%s' % self.__domain__['name']]:
            self['ACL']['group.everyone@%s' % self.__domain__['name']].append("set_number_item")
        if 'get_shopping_cart' not in self['ACL']['group.everyone@%s' % self.__domain__['name']]:
            self['ACL']['group.everyone@%s' % self.__domain__['name']].append("get_shopping_cart")
        if 'get_store_items_list' not in self['ACL']['group.everyone@%s' % self.__domain__['name']]:
            self['ACL']['group.everyone@%s' % self.__domain__['name']].append("get_store_items_list")
        
        custgrpname = 'group.customers@%s' % self.__domain__['name']
        if custgrpname not in self['ACL']:
            self['ACL'][custgrpname] = ['calculate_shipping',
                                        'add_cart_shipping',
                                        'add_cart_billing',
                                        'pay_cart',
                                        'pay_callback',
                                        'get_user_adresses']
        
        if 'calculate_shipping' not in self['ACL'][custgrpname]:
            self['ACL'][custgrpname].append("calculate_shipping")
        if 'add_cart_shipping' not in self['ACL'][custgrpname]:
            self['ACL'][custgrpname].append("add_cart_shipping")
        if 'add_cart_billing' not in self['ACL'][custgrpname]:
            self['ACL'][custgrpname].append("add_cart_billing")
        if 'pay_cart' not in self['ACL'][custgrpname]:
            self['ACL'][custgrpname].append("pay_cart")
        if 'pay_callback' not in self['ACL'][custgrpname]:
            self['ACL'][custgrpname].append("pay_callback")
        if 'get_user_adresses' not in self['ACL'][custgrpname]:
            self['ACL'][custgrpname].append("get_user_adresses")
        
        self['public'] = True
        
        self.save()
    
    @karacos._db.ViewsProcessor.isview('self', 'javascript')
    def _get_web_store_items_by_auth_(self,*args,**kw):
        """
        function(doc) {
            if (doc.public_price !== undefined && doc.store_id == "%s" && !("_deleted" in doc && doc._deleted == true)) {
                for (var auth in doc.ACL) {
                    if (doc.ACL[auth].join().search(/w_browse/) != -1) {
                        emit(auth,doc);
                    }
                }
            }
        }
        """
    @karacos._db.isaction
    def get_store_items_list(self, count=None, page=None):
        count = int(count)
        page = int(page)
        return self._get_items_list(self._get_web_store_items_by_auth_,count,page)
    
    
    @karacos._db.isaction
    def publish_node(self):
        self._publish_node()
        return {'status':'success', 'message':_("La boutique est maintenant visible de tous"), 'success': True}
    publish_node.label = _("Publier boutique")
    
    def _get_open_cart_for_customer(self,customer_id):
        self.log.debug("BEGIN _get_open_cart_for_customer")
        assert isinstance(customer_id,basestring), "Parameter person must be String - repr = %s " % customer_id
        result = None
        carts = self.__get_open_cart_for_customer__(customer_id)
        if carts.__len__() > 1:
            self.log.warn("_get_open_cart_for_customer : More than one active Cart for person")
            for cart in carts:
                cart_obj = self.db[cart.key]
                cart_obj._do_cart_cancel()
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
        self.log.debug("BEGIN _is_open_cart_for_customer")
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
        if self.__domain__.is_user_authenticated() and not self._get_customers_group().is_member(user):
            self._get_customers_group().add_user(user)
        cart = None
        customer_id = ''
        session = karacos.serving.get_session()
        if self.__domain__.is_user_authenticated():
            customer_id = user.id
        else:
            customer_id = 'anonymous.%s' % session.id
        if 'cart_id' in session:
            cart = self.db[session['cart_id']]
            if user.id != cart['customer_id']:
                if cart['customer_id'] == 'anonymous.%s' % session.id:
                    cart['customer_id'] = customer_id
                    cart.save()
                else:
                    del session['cart_id']
                    cart = None
        if cart == None:
            cart = self._get_open_cart_for_customer(customer_id)
        session['cart_id'] = cart.id
        return cart
    
    def get_open_carts_for_user(self):
        """
        Same as above, but returns an array of shoppingcarts and don't fails if more than one (useful for user to trac and remove his old commands)
        """
        user = self.__domain__.get_user_auth()
        customer_id = ''
        assert self.__domain__.is_user_authenticated() , _("Unavailable to anonymous user")
        customer_id = user.id
        if not user.belongs_to(self._get_customers_group()):
            self._get_customers_group().add_user(user)
        result = self._get_open_carts_for_customer(customer_id)
        return result
    
    @karacos._db.isaction
    def calculate_shipping(self):
        try:
            cart = self.__store__.get_open_cart_for_user()
            return {'status': 'success',
                    'success': True,
                    'data':  self._get_backoffice_node()._calculate_shipping(cart) }
        except:
            type, val, tb = sys.exc_info()
            return {'status': 'error',
                    'success': False,
                    'error': "Impossible to ship at this adress",
                    'message': "Impossible de livrer a cette adresse",
                    'errorData': traceback.format_exc().splitlines()}
        
    @karacos._db.isaction
    def view_shopping_cart(self):
        """
        """
        #person = self.__domain__._get_person_data()
        return {'status':'success', 'store_url': self._get_action_url(),'data':self.get_open_cart_for_user(),'datatype':'ShoppingCart'}

    @karacos._db.isaction
    def get_cart(self, cart_id=None):
        return {'success': True, 'result': self.db[cart_id]}
    
    @karacos._db.isaction
    def get_shopping_cart(self):
        
        result = {'success': True, 'status':'success',
                  'store_url': self._get_action_url(),
                  'data':self.get_open_cart_for_user()._get_cart_array()}
        
        return result

    @karacos._db.isaction
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
            
    @karacos._db.isaction
    def set_number_item(self,item_id=None,number=None):
        """
        sets a new number of given items in shopping Cart
        """
        cart = self.get_open_cart_for_user()
        item = self.db[item_id]
        cart['items'][item_id] = int(number)
        cart.save()
        cart.set_number_item(item,int(number))
        return {'status' :'success', 'message':_("item modifie avec succes")}
        
    
    @karacos._db.isaction
    def cancel_shopping_cart(self):
        """
        """
        #person = self.__domain__._get_person_data()
        cart = self.get_open_cart_for_user()
        cart._do_cart_cancel()
        return
        
    def _add_shipping_adr_form(self):
        user = self.__domain__._get_person_data()
        result = None
        form = {'title': _("Adresse"),
         'submit': _('Ajouter'),
         'notice': _("Nouvelle adresse de livraison"),
         'fields': [{'name':'label', 'title':'Libelle','dataType': 'TEXT'},
                 {'name':'destname', 'title':_('Nom du destinataire'),'dataType': 'TEXT'},
                 {'name':'dest1stname', 'title':_('Nom du destinataire'),'dataType': 'TEXT'},
                 {'name':'street_address', 'title':'street-address','dataType': 'TEXT','formType': 'TEXTAREA'},
                 {'name':'street_address1', 'title':'street-address1','dataType': 'TEXT','formType': 'TEXTAREA'},
                 {'name':'postal_code', 'title':'Code Postal','dataType': 'TEXT'},
                 {'name':'locality', 'title':'Ville','dataType': 'TEXT'},
                 {'name':'region', 'title':'Etat','dataType': 'TEXT'},
                 {'name':'country', 'title':'Pays','dataType': 'TEXT'},
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
                fieldlabel = "%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s" % (adr,
                                     user['adrs'][adr]['destname'],
                                     user['adrs'][adr]['dest1stname'],
                                     user['adrs'][adr]['street_address'],
                                     user['adrs'][adr]['street_address1'],
                                     user['adrs'][adr]['postal_code'],
                                     user['adrs'][adr]['locality'],
                                     user['adrs'][adr]['region'],
                                     user['adrs'][adr]['country'])
                adrsfield['values'].append({'value':adr,'label':fieldlabel})
                
            adrform['fields'].append(adrsfield)
            forms.append(adrform)
            forms.append(form)
            result = forms
        else:
            result = form
        return result
    
    @karacos._db.isaction
    def get_user_adresses(self):
        user = self.__domain__._get_person_data()
        result = {'data': []}
        if 'adrs' in user:
            c = 0
            for adr_label in user['adrs']:
                adr_record = user['adrs'][adr_label]
                adr_record['label'] = adr_label
                adr_record['id'] = c
                adr_record['user_id'] = user.id
                result['data'].append(adr_record)
                c = c + 1
        result['success'] = True
        result['status'] = 'success'
        result['total'] = len(result['data'])
        result['message'] = "%s results found" % result['total']
        return result
                
    def _add_billing_adr_form(self):
        #userojb = karacos.serving.get_session().get_user_auth()
        user = self.__domain__._get_person_data()
        result = None
        form = {'title': _("Adresse"),
         'submit': _('Ajouter'),
         'notice': _("Nouvelle adresse de facturation"),
         'fields': [{'name':'label', 'title':'Libelle','dataType': 'TEXT'},
                    {'name':'destname', 'title':_('Nom du destinataire'),'dataType': 'TEXT'},
                 {'name':'street_address', 'title':'street-address','dataType': 'TEXT','formType': 'TEXTAREA'},
                 {'name':'street_address1', 'title':'street-address1','dataType': 'TEXT','formType': 'TEXTAREA'},
                 {'name':'postal_code', 'title':'Code Postal','dataType': 'TEXT'},
                 {'name':'locality', 'title':'Ville','dataType': 'TEXT'},
                 {'name':'region', 'title':'Etat','dataType': 'TEXT'},
                 {'name':'country', 'title':'Pays','dataType': 'TEXT'},
                 {'name':'new_adr','dataType': 'HIDDEN', 'value': 'Ajouter'},
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
                fieldlabel = "%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s<br/>%s" % (adr,
                                     user['adrs'][adr]['destname'],
                                     user['adrs'][adr]['dest1stname'],
                                     user['adrs'][adr]['street_address'],
                                     user['adrs'][adr]['street_address1'],
                                     user['adrs'][adr]['postal_code'],
                                     user['adrs'][adr]['locality'],
                                     user['adrs'][adr]['region'],
                                     user['adrs'][adr]['country'])
                adrsfield['values'].append({'value':adr,'label':fieldlabel})
                
            adrform['fields'].append(adrsfield)
            forms.append(adrform)
            forms.append(form)
            result = forms
        else:
            result = form
        return result
    
    @karacos._db.isaction
    def set_adr(self,*args,**kw):
        """
        """
        user = self.__domain__._get_person_data()
        if 'use_adr' in kw:
            del kw['use_adr']
        if 'new_adr' in kw:
            del kw['new_adr']
        if 'adrs' in user:
            user['adrs'][label] = kw
        else:
            user['adrs'] = {label:kw}
        user.save()
        
    def add_cart_adr(self,user,adr_type,kw):
        """
         Add an address to shopping Cart
         adr_type : shipping / billing
        """
        assert adr_type == 'shipping' or adr_type == 'billing'
        adr_type = '%s_adr' % adr_type
        label = kw['label']
        del kw['label']
        if 'adrs' not in user:
            user['adrs'] = {}
        useadr = False
        if 'use_adr' in kw:
            del kw['use_adr']
            useadr = True
            user['adrs'][label] = kw
        if 'new_adr' in kw:
            del kw['new_adr']
            if 'adrs' in user:
                user['adrs'][label] = kw
            else:
                user['adrs'] = {label:kw}
        user.save()
        if useadr:
            cart = self.get_open_cart_for_user()
            cart[adr_type] = label #user['adrs'][label]
            cart.save()
        return user['adrs'][label]
    
    @karacos._db.isaction
    def add_cart_shipping(self,*args,**kw):
        user = self.__domain__._get_person_data()
        self.add_cart_adr(user,'shipping',kw)
        return {'status': 'success','success': True}
                
    add_cart_shipping.get_form = _add_shipping_adr_form
    add_cart_shipping.label = _("Adresse de livraison")
    
    @karacos._db.isaction
    def add_cart_billing(self,*args,**kw):
        user = self.__domain__._get_person_data()
        
        return {'success': True, 'data': self.add_cart_adr(user,'billing',kw)}
                
    add_cart_billing.get_form = _add_billing_adr_form
    add_cart_billing.label = _("Adresse de Facturation")
    
    
    @karacos._db.isaction
    def validate_cart(self):
        """
        
        """
        try:
            self.log.info("START validate_cart")
            #assert cart_id in kw, "Parameter not found, cart_id"
            cart = None
            session = karacos.serving.get_session()
            if 'cart_id' in session:
                cart = self.db[session['cart_id']]
            else:
                cart = self.get_open_cart_for_user()
                session['cart_id'] = cart.id
            if not self.__domain__.is_user_authenticated():
                return {'success': False, 'error':'User should be authenticated'}
    #            raise karacos.http.WebAuthRequired(self.__domain__,
    #                                               backlink="/%s/validate_cart"%self.get_relative_uri())
            user = self.__domain__.get_user_auth()
            if user.id != cart['customer_id']:
                assert 'anonymous.%s' % session.id == cart['customer_id'], _("Shopping cart verification failure")
                if self._is_open_cart_for_customer(user.id):
                    self.cancel_shopping_cart()
                cart['customer_id'] = user.id
                cart.save()
        
            result,type = cart._do_self_validation()
            self._get_backoffice_node()._validate_cart(cart)
            if result:
                return {'status':'success','data':cart,'datatype':'ShoppingCart', 'success':True}
            else:
                return {'message':"cart not validated, %s is missing" % type, 'type': type, 'success':False}
                
        except:
            return {'success': False, 'error':'Cart not validated', 'errorData': sys.exc_info()}
                
    def _set_services_form(self):
        result = None
        form = {'title': _("Ajouter un service de paiement"),
         'submit': _('Ajouter'),
         'fields': [{'name':'svc_name', 'title':'Nom du service','dataType': 'TEXT'},
                 ] }
        forms = []
        if 'conf_services' in self:
            
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
        default = karacos.apps['store'].providers.paypal._default_conf
        for key in default.keys():
            if key not in self['conf_services']['paypal_express']:
                self['conf_services']['paypal_express'][key] = default[key]
        self.save()
        
        
    @karacos._db.isaction
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
    set_services.label = _("Configure Services")
    def __get_services__(self):
        """
        """
        assert 'conf_services' in self, _("Services not configured for store")
        return self['conf_services'].keys()
    
    @karacos._db.isaction
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
            svc_cls = karacos.apps['store'].services.get_service(service)
            self.__services__[service] = svc_cls((self._get_service_config(service)))
        return self.__services__[service]
    
    @karacos._db.isaction
    def pay_cart(self,*args,**kw):
        """
        """
        assert 'service' in kw
        service = kw['service']
        assert service in self.__get_services__()
        userojb = karacos.serving.get_session().get_user_auth()
        person = self.__domain__._get_person_data()
        cart = self.get_open_cart_for_user()
        payment = cart._create_payment(self._get_service(service))
        return payment.do_forward()
    

    @karacos._db.isaction
    def pay_callback(self,*args,**kwds):
        """
        url handler for payment services callback
        """
        assert len(args) == 2
        payment_id,action = args
        self.log.info("pay_callback : -- %s -- %s --" % (payment_id,action))
        payment = self.db[payment_id]
        self.log.info("pay_callback ID/PAYMENT : -- %s -- %s --" % (payment_id,payment))
        result = payment.do_callback(action,*(),**kwds)
        return result
        

        
        