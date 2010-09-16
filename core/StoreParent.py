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
        if isinstance(self.__parent__, karacos.db['StoreParent']):
            self.__store__ = parent.__store__
        else:
            assert isinstance(self,karacos.db['Store']), "Invalid type parent"
            self.__store__ = self
    
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
        assert 'price' in kw
        kw['price'] = float(kw['price'])
        assert 'tax' in kw
        kw['tax'] = float(kw['tax'])
        assert 'shipping' in kw
        kw['shipping'] = float(kw['shipping'])
        self._create_child_node(data=kw,type=type)
    
    create_storeitem.form = {'title': _("Creer un produit"),
         'submit': _('Creer'),
         'fields': [{'name':'name', 'title':'Reference','dataType': 'TEXT'},
                 {'name':'type', 'title':'Type (Soft, Hard)','dataType': 'TEXT'},
                 {'name':'description', 'title':'Description','dataType': 'TEXT', 'formType': 'textarea'},
                 {'name':'price', 'title':'Prix Hors Taxes','dataType': 'TEXT'},
                 {'name':'tax', 'title':'Valeur de taxe','dataType': 'TEXT'},
                 {'name':'shipping', 'title':'Frais de port','dataType': 'TEXT'},
                 ] }