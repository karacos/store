'''
Created on 13 janv. 2010

@author: nico
'''

import KaraCos

class Store(KaraCos.Db.AppNode):
    '''
    Basic resource
    '''


    def __init__(self,parent=None,base=None,data=None,domain=None):
        assert isinstance(domain,KaraCos.Db.Domain), "domain in not type Domain"
        KaraCos.Db.AppNode.__init__(self,parent=parent,base=base,data=data)

    @staticmethod
    def create(parent=None, base=None,data=None):
        assert isinstance(data,dict)
        data['appType'] = 'Store'
        return KaraCos.Db.AppNode.create(parent=parent,base=base,data=data)