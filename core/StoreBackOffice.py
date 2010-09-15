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
    
    def _get_transactions_node(self):
        if '_transactions' not in self['childrens']:
            data = {'name':'_transactions'}
            self._create_child_node(data=data, type='Node')
        return self.db[self['childrens']['_transactions']]
    
    def _validate_cart(self, cart):
        """
        When a cart is validated, creates a record for transaction
        """
        transactions = self._get_transactions_node()
        if cart.id not in transactions['childrens']:
            # Transaction is not registered
            data = {'name': cart.id, 'status':'pending', 'log': []}
            transactions._create_child_node(data=data,type='Node')
        else:
            transaction = transactions.db[transactions['childrens'][cart.id]]
        transaction['log'].append({'tst':datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                                   'action':'validate_cart', 'message':'cart validation'})
        transaction.save()
    
    def _set_payment_created(self, cart, payment):
        """
        When a payment is created, store in transaction record the payment_id
        """
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