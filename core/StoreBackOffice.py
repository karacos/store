'''
Created on 9 sept. 2010

@author: nico
'''
import karacos
import datetime
class StoreBackOffice(karacos.db['WebNode']):
    '''
    BackOffice resource
    '''


    def __init__(self,parent=None,base=None,data=None):
        assert isinstance(parent,karacos.db['Store']), "parent of backoffice is a store"
        karacos.db['WebNode'].__init__(self,parent=parent,base=base,data=data)
        self.__store__ = parent

    @staticmethod
    def create(parent=None, base=None,data=None, owner=None):
        """
        StoreBackOffice is created with a distinct base
        """
        assert isinstance(parent,karacos.db['Store']), "domain in not Traderzic Domain"
        assert isinstance(data,dict)
        if 'WebType' not in data:
            data['WebType'] = 'StoreBackOffice'
        data['name'] = '_backoffice'
        return karacos.db['WebNode'].create(parent=parent,base=base,data=data)
    
    @karacos._db.isaction
    def rename(self):
        assert False, "Rename backoffice is not allowed"
    
    @karacos._db.isaction
    def set_shipping_rates(self,country="France",weight=None,price=None):
        """
        
        """
        weight = int(weight)
        price = int(price)
        if 'shipping_rates' not in self:
            self['shipping_rates'] = {country: {weight:price}}
        else:
            if country not in self['shipping_rates']:
                self['shipping_rates'][country] = {weight:price}
            else:
                self['shipping_rates'][country][weight] = price
            
        self.save()
        return {'success': True}
    
    @karacos._db.ViewsProcessor.isview('self', 'javascript')
    def _get_shopping_carts_(self,store_id,*args,**kw):
        """ //%s
        function(doc) {
            if (doc.type == "ShoppingCart" && doc.parent_id == "%s" && !("_deleted" in doc && doc._deleted == true)) {
                emit(doc.status, doc);
            }
        }
        """
    
    @karacos._db.isaction
    def get_shopping_carts(self,*args,**kw):
        return {'success': True, 'data': self._get_shopping_carts()}
    
    def _get_shopping_carts(self,*args,**kw):
        """
        Returns the list of shopping carts
        """
        result = []
        carts = self._get_shopping_carts_(self.__store__.id)
        for cart in carts:
            result.append(cart.value)
        return result
    
    def _purge_canceled_carts(self):
        """
        """
        carts = self._get_shopping_carts_(self.__store__.id, *(),**{'key':'cancel'})
        rmcount = 0
        for cart in carts:
            rmcount+=1
            del self.__store__.db[cart.value['_id']]
        return "%s canceled carts deleted" % rmcount
    
    def _purge_inactive_carts(self):
        """
        """
        carts = self._get_shopping_carts_(self.__store__.id, *(),**{'keys':['open','process_pay']})
        rmcount = 0
        purge_before = datetime.datetime.now() - datetime.timedelta(2) # more than two day old
        for cart in carts:
            cart_date = datetime.datetime.strptime(cart.value['last_modification_date'],'%Y-%m-%dT%H:%M:%S')
            if cart_date < purge_before:
                rmcount+=1
                del self.__store__.db[cart.value['_id']]
        return "%s inactive carts deleted" % rmcount
    
    @karacos._db.isaction
    def purge_carts(self,criteria=None):
        if criteria == "canceled":
            return {'success': True, 'message': self._purge_canceled_carts()}
        if criteria == "inactive":
            return {'success': True, 'message': self._purge_inactive_carts()}
        return {'success': False, 'message': "Nothing to do without criteria"}
    
    def _get_shipping_rates(self):
        if 'shipping_rates' not in self:
            self['shipping_rates'] = {}
        self.save()
        result = []
        for country in self['shipping_rates'].keys():
            for weight in self['shipping_rates'][country].keys():
                result.append({'country': country, 'weight': weight, 'price': self['shipping_rates'][country][weight]})
        return result
    
    @karacos._db.isaction
    def get_shipping_rates(self):
        return {'success': True, 'data': self._get_shipping_rates()}
    
    def _get_transactions_node(self):
        if '_transactions' not in self['childrens']:
            data = {'name':'_transactions'}
            self._create_child_node(data=data, type='Node')
        return self.db[self['childrens']['_transactions']]
    

    
    def _reserve_item(self,item,cart):   
        assert isinstance(item, karacos.db['StoreItem'])
        assert isinstance(cart, karacos.db['ShoppingCart'])
        assert 'item_stock' in self, 'No stock data'
        assert item.id in self['item_stock'], 'No stock registered for item'
        number = cart['items'][item.id]
        assert self['item_stock'][item.id] >= number, "Not enough stock"
        item['stock'] = item['stock'] - number
        item.save()
        if 'reserved' not in self:
            self['reserved'] = {}
        if item.id not in self['reserved']:
            self['reserved'][item.id] = {}
        cur_tmp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        self['reserved'][item.id][cart.id] = number
        self.save()
        return
    
    def _reserved_cancel(self,item,cart):
        ""
        assert isinstance(item, karacos.db['StoreItem'])
        assert isinstance(cart, karacos.db['ShoppingCart'])
        assert 'item_stock' in self, 'No stock data'
        assert item.id in self['item_stock'], 'No stock registered for item'
        assert 'reserved' in self, 'No reserved parts'
        assert item.id in self['reserved'], 'No reservation for this item'
        assert cart.id in self['reserved'][item.id], 'item not reserved for this cart'
        assert self['reserved'][item.id][cart.id] == cart['items'][item.id], 'Inconsistent data'
        number = cart['items'][item.id]
        item['stock'] = item['stock'] + number
        item.save()
        del self['reserved'][item.id][cart.id]
        self.save()
    
    def _calculate_shipping(self,cart):
        assert "shipping_rates" in self, "No shipping rates set for this store"
        assert cart._get_shipping_adr()['country'] in self['shipping_rates']
        return { 'shipping': cart._get_cart_array()['shipping'], 'adress' : cart._get_shipping_adr()}
        
    def _get_shipping_rate(self,country,weight):
        wkeys = map(int,self['shipping_rates'][country].keys())
        wkeys.sort()
        swkeys = [] + wkeys
        wkeys.append(weight)
        wkeys.sort()
        indexkey = wkeys.index(weight) 
        if indexkey >= len(swkeys):
            indexkey = indexkey -1
        
        indexweight = swkeys[indexkey]
        return self['shipping_rates'][country][str(indexweight)]
    
    def _item_payed(self,item,cart):
        ""
        assert isinstance(item, karacos.db['StoreItem'])
        assert isinstance(cart, karacos.db['ShoppingCart'])
        #assert 'item_stock' in self, 'No stock data'
        #assert item.id in self['item_stock'], 'No stock registered for item'
        #assert 'reserved' in self, 'No reserved parts'
        #assert item.id in self['reserved'], 'No reservation for this item'
        #assert cart.id in self['reserved'][item.id], 'item not reserved for this cart'
        #assert self['reserved'][item.id][cart.id] == cart['items'][item.id], 'Inconsistent data'
        #del self['reserved'][item.id][cart.id]
        number = cart['items'][item.id]
        item['stock'] = item['stock'] - number
        item.save()
        self.save()
    
    def _reserved_payed(self,item,cart):
        ""
        assert isinstance(item, karacos.db['StoreItem'])
        assert isinstance(cart, karacos.db['ShoppingCart'])
        assert 'item_stock' in self, 'No stock data'
        assert item.id in self['item_stock'], 'No stock registered for item'
        assert 'reserved' in self, 'No reserved parts'
        assert item.id in self['reserved'], 'No reservation for this item'
        assert cart.id in self['reserved'][item.id], 'item not reserved for this cart'
        assert self['reserved'][item.id][cart.id] == cart['items'][item.id], 'Inconsistent data'
        del self['reserved'][item.id][cart.id]
        self.save()
       
    def _validate_cart(self, cart):
        """
        When a cart is validated, creates a record for transaction
        """
        self.log.debug("_validate_cart START")
        transactions = self._get_transactions_node()
        if cart.id not in transactions['childrens']:
            # Transaction is not registered
            data = {'name': cart.id, 'status':'pending', 'log': []}
            self.log.debug("_validate_cart creating transaction '%s'" % cart.id)
            transactions._create_child_node(data=data,type='Node')
        transaction = transactions.db[transactions['childrens'][cart.id]]
        transaction['log'].append({'tst':datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                                   'action':'validate_cart', 'message':'cart validation'})
        transaction.save()
    
    def _set_payment_created(self, cart, payment):
        """
        When a payment is created, store in transaction record the payment_id
        """
        self.log.debug("_set_payment_created START")
        transactions = self._get_transactions_node()
        assert cart.id in transactions['childrens'], _("Corruption in process; transaction is not registered")
        transaction = transactions.db[transactions['childrens'][cart.id]]
        transaction['bill'] = cart._get_bill_data()
        transaction['active_payment'] = {'id': payment.id,'service': payment['service']['name'],'creation_date':payment['creation_date']}
        transaction['log'].append({'tst':datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                                   'action':'payment_created', 'creation_date':payment['creation_date'],
                                   'payment_id':payment.id,'payment_service': payment['service']})
        transaction.save()
        
    
    def _set_payment_validated(self, cart, payment):
        """
        When the payment is validated by thirdparty, update transaction record status
        """
        self.log.debug("_set_payment_validated START")
        transactions = self._get_transactions_node()
        assert cart.id in transactions['childrens'], _("Corruption in process; transaction is not registered")
        transaction = transactions.db[transactions['childrens'][cart.id]]
        assert transaction['active_payment']['id'] == payment.id, _("Payment id doesn't match")
        transaction['status'] = 'payment_validated'
        transaction['log'].append({'tst':datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                                   'action':'payment_validated', 'creation_date':payment['creation_date'],
                                   'payment_id':payment.id,'payment_service': payment['service']})
        transaction.save()
        
        
    
    def _set_payment_cancelled(self, cart, payment):
        """
        When the payment is cancelled, update transaction record status
        """
        transactions = self._get_transactions_node()
        assert cart.id in transactions['childrens'], _("Corruption in process; transaction is not registered")
        transaction = transactions.db[transactions['childrens'][cart.id]]
        assert transaction['active_payment']['id'] == payment.id, _("Payment id doesn't match")
        transaction['status'] = 'payment_cancelled'
        transaction['log'].append({'tst':datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                                   'action':'payment_cancelled', 'creation_date':payment['creation_date'],
                                   'payment_id':payment.id,'payment_service': payment['service']})
        transaction.save()