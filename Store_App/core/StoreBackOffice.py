'''
Created on 9 sept. 2010

@author: nico
'''
import KaraCos

class StoreBackOffice(KaraCos.Db.WebNode):
    '''
    BackOffice resource
    '''


    def __init__(self,parent=None,base=None,data=None):
        assert isinstance(parent,KaraCos.Db.Store), "parent of backoffice is a store"
        KaraCos.Db.WebNode.__init__(self,parent=parent,base=base,data=data)

    @staticmethod
    def create(parent=None, base=None,data=None, owner=None):
        """
        StoreBackOffice is created with a distinct base
        """
        assert isinstance(parent,KaraCos.Db.Store), "domain in not Traderzic Domain"
        assert isinstance(data,dict)
        if 'WebType' not in data:
            data['WebType'] = 'StoreBackOffice'
        data['name'] = '_backoffice'
        return KaraCos.Db.WebNode.create(parent=parent,base=True,data=data,owner=owner)
    
    @KaraCos.Db.isaction
    def rename(self):
        assert False, "Rename backoffice is not allowed"
    
    def _get_transactions_node(self):
        if '_transactions' not in self['childrens']:
            data = {'name':'_transactions'}
            self._create_child_node(data=data, type='Node')
        return self['childrens']['_transactions']
    
    def _validate_cart(self, cart):
        """
        When a cart is validated
        """
        data = {'name': cart.id, 'bill':cart._get_bill_data()}
        self._get_transactions_node()._create_child_node()
    
    def _set_payment_created(self, cart, payment):
        """
        When a payment is created
        """
    
    def _set_payment_validated(self, cart, payment):
        """
        When the payment is validated by thirdparty
        """
    
    def _set_payment_cancelled(self, cart, payment):
        """
        When the payment is cancelled
        """