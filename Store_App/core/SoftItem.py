'''
Created on 1 juin 2010

@author: nico
'''


__author__ = "Nicolas Karageuzian"
__contributors__ = []

import KaraCos
_ = KaraCos._
fields = KaraCos._Rpc.DynForm.fields

class SoftItem(KaraCos.Db.StoreItem):
    '''
    Item with no shipping
    '''

    def __init__(self,parent=None,base=None,data=None):
        KaraCos.Db.StoreItem.__init__(self,parent=parent,base=base,data=data)
    
    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent,KaraCos.Db.StoreParent)
        if 'WebType' not in data:
            data['WebType'] = 'SoftItem'
        return KaraCos.Db.StoreItem.create(parent=parent,base=base,data=data,owner=owner)