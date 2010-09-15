'''
Created on 1 juin 2010

@author: nico
'''


__author__ = "Nicolas Karageuzian"
__contributors__ = []

import karacos

class SoftItem(karacos.db['StoreItem']):
    '''
    Container for soft Store items (like access to a file or piece of software, or site feature)
    is still abstract
    Item with no shipping
    '''

    def __init__(self,parent=None,base=None,data=None):
        karacos.db['StoreItem'].__init__(self,parent=parent,base=base,data=data)
    
    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent,karacos.db['StoreParent'])
        assert 'WebType' in data, "Could not instanciate abstract type SoftItem"
        return karacos.db['StoreItem'].create(parent=parent,base=base,data=data)
    