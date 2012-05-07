'''
Created on 13 janv. 2010

@author: nico
'''
from uuid import uuid4
import simplejson as json
import karacos, sys

class ShoppingCart(karacos.db['Node']):
    '''
    Basic resource
    '''


    def __init__(self,parent=None,base=None,data=None):
        karacos.db['Node'].__init__(self,parent=parent,base=base,data=data)
        self.__parent__ = parent
        self.__store__ = parent
        if 'items' not in self:
            self['items'] = {}
        self.save()

    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(parent,karacos.db['Store']), "Parent type invalid : %s - Should be Store" % type(parent)
        assert isinstance(data,dict)
        if 'type' not in data:
            data['type'] = 'ShoppingCart'
        result = karacos.db['Node'].create(parent=parent,base=False,data=data)
        return result
    
    def _add_item(self,*args,**kw):
        assert self['status'] == 'open'
        assert 'item' in kw
        assert isinstance(kw['item'],karacos.db['StoreItem'])
        assert 'number' in kw
        number = int(kw['number'])
        if 'cart_array' not in self:
            self['cart_array'] = []
        if 'weight' not in kw['item']:
            kw['item']['weight'] = 0
        price = 0
        net_price = 0
        tax = 0
        if 'price' not in kw['item'] and 'public_price' in kw['item'] :
            price = float(kw['item']['public_price'])
            net_price = price
        elif 'price' in kw['item'] and kw['item']['price'] == 0 and 'public_price' in kw['item']:
            price = float(kw['item']['public_price'])
            net_price = price
        elif 'price' in kw['item'] and not kw['item']['price'] == 0:
            tax = float(kw['item']['tax'])
            net_price = float(kw['item']['price'])
            price = net_price + net_price * tax
        self['cart_array'].append({'id': kw['item']['_id'],
                                        'name':kw['item']['name'],
                                        'title': kw['item'].__get_title__(),
                                        'tax':"%.2f" % tax,
                                        'price':"%.2f" % price,
                                        'net_price': "%.2f" % net_price,
                                        'weight': int(int(kw['item']['weight']) * number),
                                        'number':number,
                                        'total': "%.2f" % float(price * number),
                                        'tax_total': "%.2f" % float(tax * net_price * number),
                                        'net_total':"%.2f" %  float(net_price * number)})
        self.save()
        return True
    
    def set_number_item(self,item,number):
        """
        """
        def find_item(mapelem):
            if item.id == mapelem['id']:
                return mapelem
        def red_it(a,b):
            if a != None:
                return a
            if b != None:
                return b
        found = None
        if 'cart_array' not in self:
            self['cart_array'] = []
        else:
            if len(self['cart_array']) > 0:
                found = reduce(red_it,map(find_item, self['cart_array']))
        if found == None:
            self._add_item(*(),**{'item': item, 'number': number})
        else:
            it_id =  self['cart_array'].index(found)
            self['items'][item.id] = number
            found['number'] =  number
            if 'weight' not in item:
                item['weight'] = 0
                item.save()
            found['weight'] = "%d" % int(item['weight'] * self['items'][item.id])
            found['net_total'] = "%.2f" % (float(item['price']) * int(self['items'][item.id]))
            found['tax_total'] = "%.2f" % float(float(item['tax']) * float(item['price']) * self['items'][item.id])
            found['total'] = "%.2f" % ((float(item['price'])+ float(item['tax']) * float(item['price'])) * int(self['items'][item.id]))
            found['net_total'] = "%.2f" % ( float(item['price']) * self['items'][item.id])
            self['cart_array'][it_id] = found
            self.save()
        
    @karacos._db.ViewsProcessor.isview('self','javascript')
    def __get_cart_items_array__(self, store):
        """//%s
        function(doc) {
            if ( doc.parent_id == "%s" && !("_deleted" in doc && doc._deleted == true))
                    emit(doc._id, doc)
        }
        """
      
    @karacos._db.ViewsProcessor.isview('self','javascript')
    def __get_cart_items_array__(self, store):
        """//%s
        function(doc) {
            if ( doc.parent_id == "%s" && !("_deleted" in doc && doc._deleted == true))
                    emit(doc._id, doc)
        }
        """
    
    def _get_cart_array(self):
        self._update_item()
        if 'cart_array' not in self:
            self['cart_array'] = []
            self.save()
        result = {'items': self['cart_array'], 'cart_total':0, 'cart_net_total':0, 'cart_tax_total':0, 'cart_total_weight': 0, 'customer_email': self.get_customer_email()}
        for item in self['cart_array']:
            try:
                result['cart_total'] = "%.2f" % (float(result['cart_total']) + float(item['total']))
                result['cart_tax_total'] = "%.2f" % (float(result['cart_tax_total']) + float(item['tax_total']))
                result['cart_net_total'] = "%.2f" % (float(result['cart_net_total']) + float(item['net_total']))
                result['cart_total_weight'] = int(result['cart_total_weight']) + int(item['weight']) * int(self['items'][item['id']])
            except:
                self.log.log_exc( sys.exc_info(),'warn')
        if 'billing_adr' in self:
            result['billing_adr'] = self['billing_adr']
            result['billing_adress'] = self._get_billing_adr()
        if 'shipping_adr' in self:
            try:
                result['shipping'] = self.__store__._get_backoffice_node()._get_shipping_rate(self._get_shipping_adr()['country'].lower(),int(result['cart_total_weight']))
                result['cart_total'] = "%.2f" % (float(result['cart_total']) + float(result['shipping']))
                # result['cart_net_total'] = "%.2f" % (float(result['cart_net_total']) + float(result['shipping']))
                result['shipping_adr'] = self['shipping_adr']
                result['shipping_adress'] = self._get_shipping_adr()
            except:
                self.log.log_exc( sys.exc_info(),'warn')
                result['shipping'] = "Impossible de livrer a l'adresse renseignee"
        else:
            result['shipping'] = "Pas d'adresse de livraison..."
        
        return result
     
    def _get_bill_data(self):
        result = {'items':{},'total':0, 'net_total':0, 'tax_total':0}
        cart_array = self._get_cart_array()
        itemscount = len(cart_array['items'])

        while itemscount > 0: #__get_cart_items_array__(self.__store__.id,*(), **{'keys':self['items'].keys()}):
            itemscount = itemscount - 1
            item = cart_array['items'][itemscount]
            result['items'][item['id']] = {'name':item['name'],
                                         'title': item['title'],
                                         'net_price': item['net_price'],
                                            'tax':item['tax'],
                                            'tax_amt': "%.2f" % (float(item['tax']) * float(item['net_price'])),
                                            'price': item['price'],
                                            'number':item['number'],
                                            'total': item['total'],
                                            'tax_total': item['tax_total'],
                                            'net_total': item['net_total']}
        result['shipping'] = cart_array['shipping']
        result['net_total'] =  cart_array['cart_net_total']
        result['tax_total'] = cart_array['cart_tax_total']
        result['total'] = cart_array['cart_total']
        if 'shipping_adress' in self:
            result['shipping_adress'] = self['shipping_adress']
        if 'shipping_adress' in self:
            result['shipping_adress'] = self['shipping_adress']
        return result
    
    def _get_billing_adr(self):
        """
        """
        if 'billing_adr' not in self:
            return None
        
        if self['customer_id'].find("anonymous") >= 0:
            return None
        user = self.__domain__.db[self['customer_id']]
        userdata = self.__domain__._get_person_data_user(user)
        return userdata['adrs'][self['billing_adr']]
    
    
    def _get_shipping_adr(self):
        """
        """
        if 'shipping_adr' not in self:
            return None
        
        if self['customer_id'].find("anonymous") >= 0:
            return None
        user = self.__domain__.db[self['customer_id']]
        userdata = self.__domain__._get_person_data_user(user)
        return userdata['adrs'][self['shipping_adr']]
    
    def _do_self_validation(self):
        """
        Check if enough data in cart (regarding each item requirement)
        """
        
            # Billing adress is required
            # raise karacos.http.DataRequired(self.__store__,self.__store__.add_cart_billing,
            #                                backlink = "/%s/validate_cart"%self.__store__.get_relative_uri(),
            #                                message = "Validate billing")
        result = None   
        for item_key in self['items'].keys() :
            try:
                # TODO redefine _do_cart_validation signature and imns
                result = self.db[item_key]._do_cart_validation(self)
            except:
                return (False, 'unknown')
        if 'billing_adr' not in self:
            return (False,'billing')
        if result[0]:
            self['validated'] = True
            self.save()
        return result
    
    def _add_shipping_adress_(self,adress):
        ""
    
    @karacos._db.ViewsProcessor.isview('self','javascript')
    def __get_active_payment__(self):
        """
        function(doc){
         if(doc.parent_id == "%s" && (doc.status == "active" || doc.status == "validated"))
             emit(doc._id,doc)
        }
        """
    
    def get_customer_email(self):
        """ Retrieve customer's email, none otherwise """
        try:
            if 'contact_mail' not in self:
                self['contact_mail'] = self.db[self['customer_id']]._get_email()
                self.save()
            return self['contact_mail']
        except:
            return None
    
    def set_customer_email(self,email):
        self['contact_mail'] = email
        self.save()
        return {"success": True, 'message': "Email registered for shopping_cart"}
        
    def _get_active_payment(self):
        """
        """
        result = None
        payments = self.__get_active_payment__()
        assert payments.__len__() <= 1, "payments : More than one active payments for Cart"
        if payments.__len__() == 1:
            for payment in payments:
#                    KaraCos._Db.log.debug("get_child_by_name : db.key = %s db.value = %s" % (child.key,domain.value) )
                result = self.db[payment.key]
        else:
            return None
    
        return result
    
    def _has_active_payment(self):
        """
        """
        return False
    
    def _create_payment(self,service):
        """
        service : name of the service : 'papal_express'
        """
        self.log.debug("_create_payment START")
        assert not self._has_active_payment()
        name = "%s" % uuid4().hex
        data = {'name':name, 'cart_id':self.id , 'service': {'name':service['_name']} ,'status':'active'}
        self._create_child_node(data=data,type='Payment')
        self.log.debug("Payment created with name '%s'" % name)
        self['status'] = 'process_pay'
        self['payment_id'] = name
        self.save()
        session = karacos.serving.get_session()
        del session['cart_id']
        result  = self.db[self['childrens'][name]]
        self.__store__._get_backoffice_node()._validate_cart(self)
        self.__store__._get_backoffice_node()._set_payment_created(self,result)
        return result
    
    def _do_payment_validated(self,payment):
        self['status'] = 'payment_ok'
        self['valid_payment'] = payment.id
        self.save()
        self.__store__._get_backoffice_node()._set_payment_validated(self,payment)
        for item_key in self['items'].keys() :
            self.db[item_key]._do_cart_processing(self)
        self.save()
        session = karacos.serving.get_session()
        if 'cart_id' in session:
            del session['cart_id']
    
    def _do_cart_cancel(self):
        for item_key in self['items'].keys() :
            self.db[item_key]._do_cart_cancel(self)
        self['status'] = 'cancel'
        self.save()
        session = karacos.serving.get_session()
        if 'cart_id' in session:
            del session['cart_id']
        
    
    def _do_payment_cancelled(self,payment):
        self._do_cart_cancel()
        self['is_open'] = 'true'
        self['status'] = 'payment_ko'
        self.save()
        self.__store__._get_backoffice_node()._set_payment_cancelled(self,payment)
        session = karacos.serving.get_session()
        if 'cart_id' in session:
            del session['cart_id']