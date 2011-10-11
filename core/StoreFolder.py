'''
Created on 26 mars 2010
'''
__author__ = "Nicolas Karageuzian"
__contributors__ = []

import karacos

class StoreFolder(karacos.db['StoreParent']):
    '''
    Container for Store items
    '''
    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent,karacos.db['StoreParent'])
        if 'WebType' not in data:
            data['WebType'] = 'StoreFolder'
        return karacos.db['WebNode'].create(parent=parent,base=False,data=data)

    def __init__(self,parent=None,base=None,data=None):
        karacos.db['StoreParent'].__init__(self,parent=parent,base=base,data=data)