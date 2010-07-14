'''
Created on 26 mars 2010
'''
__author__ = "Nicolas Karageuzian"
__contributors__ = []

import KaraCos
_ = KaraCos._
fields = KaraCos._Rpc.DynForm.fields

class StoreFolder(KaraCos.Db.StoreParent):
    '''
    Container for Store items
    '''

    def __init__(self,parent=None,base=None,data=None):
        KaraCos.Db.StoreParent.__init__(self,parent=parent,base=base,data=data)
    
    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent,KaraCos.Db.StoreParent)
        if 'WebType' not in data:
            data['WebType'] = 'StoreFolder'
        return KaraCos.Db.WebNode.create(parent=parent,base=False,data=data,owner=owner)
  
  