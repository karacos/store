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
        assert 'number' in kw
        assert 'item' in kw
        number = int(kw['number'])
        assert isinstance(kw['item'],karacos.db['StoreItem'])
        if kw['item'].id not in self['items']:
            self['items'][kw['item'].id] = number
        else:
            self['items'][kw['item'].id] = self['items'][kw['item'].id] + number
        if 'cart_array' not in self:
            self['cart_array'] = []
        if 'weight' not in kw['item']:
            item['weight'] = 0
        price = 0
        if 'price' not in kw['item'] and 'public_price' in kw['item'] :
            price = float(kw['item']['public_price'])
        elif 'price' in kw['item'] and kw['item']['price'] == 0 and 'public_price' in kw['item']:
            price = float(kw['item']['public_price'])
        elif 'price' in kw['item'] and not kw['item']['price'] == 0:
            price = float(kw['item']['price']) + float(kw['item']['tax']) * float(kw['item']['price'])
        self['cart_array'].append({'id': kw['item']['_id'],
                                        'name':kw['item']['name'],
                                        'title': kw['item']['title'],
                                        'tax':float(kw['item']['tax']),
                                        'price':price,
                                        'net_price': price,
                                        'weight': int(kw['item']['weight']) * int(self['items'][kw['item'].id]),
                                        'number':number,
                                        'total': price * number,
                                        'tax_total': 'N/A',
                                        'net_total': price * number})
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
            self._add_item(*(),**{'item': item, 'number':number})
        else:
            it_id =  self['cart_array'].index(found)
            self['items'][item.id] = number
            found['number'] = number
            found['weight'] = item['weight'] * self['items'][item.id]
            found['total'] =  item['price'] * self['items'][item.id],
            found['tax_total'] =  item['tax'] * item['price'] * self['items'][item.id],
            found['net_total'] = (item['price'] + item['tax'] * item['price']) * self['items'][item.id]
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
                
#        if 'validated' not in self:
#            try:
#                for item_key in self['items'].keys() :
#                    self.db[item_key]._do_cart_validation(self)
#                result['requires'] = 'billing'
#            except:
#                result['requires'] = 'shipping'
#        else:
#            result['requires'] = 'meet'
        if 'cart_array' not in self:
            self['cart_array'] = []
            self.save()
        result = {'items': self['cart_array'], 'cart_total':0, 'cart_net_total':0, 'cart_tax_total':0, 'cart_total_weight': 0}
        for item in self['cart_array']:
            try:
                result['cart_total_weight'] = int(result['cart_total_weight']) + int(item['weight']) * int(self['items'][item['id']])
                result['cart_total'] = result['cart_total'] + float(item['total'])
                result['cart_tax_total'] = result['cart_tax_total'] + float(item['tax_total'])
                result['cart_net_total'] = result['cart_net_total'] + float(item['net_total'])
            except:
                self.log.log_exc( sys.exc_info(),'warn')
        if 'billing_adr' in self:
            result['billing_adr'] = self['billing_adr']
            result['billing_adress'] = self._get_billing_adr()
        if 'shipping_adr' in self:
            try:
                result['shipping'] = self.__store__._get_backoffice_node()._get_shipping_rate(self._get_shipping_adr()['country'],result['cart_total_weight'])
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
        for item in self.__get_cart_items_array__(self.__store__.id,*(), **{'keys':self['items'].keys()}):
            if 'price' not in item.value and 'public_price' in item.value:
                item.value['price'] = item.value['public_price']
            result['items'][item.key] = {'name':item.value['name'],
                                         'title': item.value['title'],
                                            'tax':item.value['tax'],
                                            'price':item.value['price'],
                                            'number':self['items'][item.key],
                                            'total': item.value['price'] * self['items'][item.key],
                                            'tax_total': item.value['tax'] * item.value['price'] * self['items'][item.key],
                                            'net_total': (item.value['price'] + item.value['tax'] * item.value['price']) * self['items'][item.key]}
            result['total'] = result['total'] + result['items'][item.key]['total']
            result['tax_total'] = result['tax_total'] + result['items'][item.key]['tax_total']
            result['net_total'] = result['net_total'] + result['items'][item.key]['net_total']
        if 'billing_adr' in self:
            result['billing_adr'] = self['billing_adr']
        if 'shipping_adr' in self:
            result['shipping_adr'] = self['shipping_adr']
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
        if 'billing_adr' not in self:
            # Billing adress is required
            raise karacos.http.DataRequired(self.__store__,self.__store__.add_cart_billing,
                                            backlink = "/%s/validate_cart"%self.__store__.get_relative_uri(),
                                            message = "Validate billing")
        for item_key in self['items'].keys() :
            self.db[item_key]._do_cart_validation(self)
        self['validated'] = True
        self.save()
    
    def _add_shipping_adress_(self,adress):
        ""
    def __get_active_payment__(self):
        """
        function(doc){
         if(doc.parent_id == "%s" && doc.status == "active")
             emit(doc._id,doc)
        }
        """
        
    def _get_active_payment(self):
        """
        """
        result = None
        payments = self.__get_active_payment__()
        assert payments.__len__() <= 1, "payments : More than one active payments for Cart"
        if payments.__len__() == 1:
            for payment in payments:
#                    KaraCos._Db.log.debug("get_child_by_name : db.key = %s db.value = %s" % (child.key,domain.value) )
                result = self.db[payments.key]
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
        self['is_open'] = 'true'
        self['status'] = 'payment_ko'
        self.save()
        self.__store__._get_backoffice_node()._set_payment_cancelled(self,payment)
        session = karacos.serving.get_session()
        del session['cart_id']