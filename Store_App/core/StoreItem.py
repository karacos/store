'''
Created on 13 janv. 2010

@author: nico
'''


'''
Created on 13 janv. 2010

@author: nico
'''

import KaraCos

class StoreItem(KaraCos.Db.Resource):
    '''
    Basic resource
    '''


    def __init__(self,parent=None,base=None,data=None,domain=None):
        assert isinstance(domain,KaraCos.Db.Domain), "domain in not type Domain"
        KaraCos.Db.Resource.__init__(self,parent=parent,base=base,data=data)

    @staticmethod
    def create(parent=None, base=None,data=None):
        assert isinstance(data,dict)
        if 'WebType' not in data:
            data['WebType'] = 'StoreItem'
        return KaraCos.Db.Resource.create(parent=parent,base=base,data=data)