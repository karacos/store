'''
Created on 1 juin 2010

@author: nico
'''


__author__ = "Nicolas Karageuzian"
__contributors__ = []

import KaraCos
_ = KaraCos._
fields = KaraCos._Rpc.DynForm.fields

class HardItem(KaraCos.Db.StoreItem):
    '''
    Container for Store items as a piece of hard, material part or stuff
    '''

    def __init__(self,parent=None,base=None,data=None):
        KaraCos.Db.StoreItem.__init__(self,parent=parent,base=base,data=data)
    
    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent,KaraCos.Db.StoreParent)
        if 'WebType' not in data:
            data['WebType'] = 'HardItem'
        return KaraCos.Db.StoreItem.create(parent=parent,base=base,data=data,owner=owner)
    
    def _do_cart_validation(self,cart):
        """
        such an item requires shipping adress
        """
        if 'shipping_adr' not in cart:
            raise KaraCos._Core.exception.DataRequired("Validate shipping","","/%s?method=validate_cart"%self.__store__.get_relative_uri(),self.__store__,self.__store__.add_cart_shipping)