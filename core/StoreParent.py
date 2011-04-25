'''
Created on 26 mars 2010
'''
__author__ = "Nicolas Karageuzian"
__contributors__ = []

import karacos

class StoreParent(karacos.db['WebNode']):
    '''
    Basic container for Store, abstract
    '''
    def __init__(self,parent=None,base=None,data=None):
        karacos.db['WebNode'].__init__(self,parent=parent,base=base,data=data)
        if isinstance(self, karacos.db['Store']):
            self.__store__ = self
        else:
            assert isinstance(self.__parent__,karacos.db['StoreParent']), "Invalid type parent"
            self.__store__ = parent.__store__
        if 'store_id' not in self:
            self['store_id'] = self.__store__.id
            self.save()
        
    
    @karacos._db.isaction
    def create_store_folder(self,*args,**kw):
        self._create_child_node(data=kw,type='StoreFolder')
    
    create_store_folder.form = {'title': _("Creer un produit"),
         'submit': _('Creer'),
         'fields': [{'name':'name', 'title':'Nom','dataType': 'TEXT'},
                 {'name':'description', 'title':'Description','dataType': 'TEXT', 'formType': 'textarea'}
                 ] }
    
    @karacos._db.isaction
    def create_storeitem(self,*args,**kw):
        assert 'type' in kw
        assert kw['type'] == 'Soft' or kw['type'] == 'Hard'
        type = '%sItem' % kw['type']
        del kw['type']
        assert 'buy_cost' in kw
        kw['buy_cost'] = float(kw['buy_cost'])
        assert 'min_sell_price' in kw
        kw['min_sell_price'] = float(kw['min_sell_price'])
        assert 'public_price' in kw
        kw['public_price'] = float(kw['public_price'])
        assert 'title' in kw
        kw['title'] = kw['title']
        assert 'weight' in kw
        kw['weight'] = float(kw['weight'])
        assert 'tax' in kw
        kw['tax'] = float(kw['tax'])
        assert 'stock' in kw
        kw['stock'] = float(kw['stock'])
        self._create_child_node(data=kw,type=type)
        return {'success': True, 'message':'Node cree avec succes'}
    
    create_storeitem.form = {'title': _("Creer un produit"),
         'submit': _('Creer'),
         'fields': [{'name':'name', 'title':'Reference','dataType': 'TEXT'},
                 {'name':'type', 'title':'Type (Soft, Hard)','dataType': 'TEXT'},
                 {'name':'description', 'title':'Description','dataType': 'TEXT', 'formType': 'textarea'},
                 {'name':'price', 'title':'Prix Hors Taxes','dataType': 'TEXT'},
                 {'name':'tax', 'title':'Valeur de taxe','dataType': 'TEXT'},
                 {'name':'shipping', 'title':'Frais de port','dataType': 'TEXT'},
                 ] }