'''
Created on 13 janv. 2010

@author: nico
'''


'''
Created on 13 janv. 2010

@author: nico
'''
import sys
import KaraCos
_ = KaraCos._
fields = KaraCos._Rpc.DynForm.fields

class StoreItem(KaraCos.Db.Resource):
    '''
    Basic resource
    '''

    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent,KaraCos.Db.Store)
        assert isinstance(parent.__domain__,KaraCos.Db.MDomain)
        # assert owner.get_auth_id()
        if 'WebType' not in data:
            data['WebType'] = 'StoreItem'
        
        return KaraCos.Db.Resource.create(parent=parent,base=base,data=data,owner=owner)
    


    def __init__(self,parent=None,base=None,data=None,domain=None):
        assert isinstance(parent,KaraCos.Db.Store)        
        KaraCos.Db.Resource.__init__(self,parent=parent,base=base,data=data)
        self.__store__ = parent
    
    
    def _edit_storeitem_form(self):
        return {'title': _("Modifier le produit"),
         'submit': _('Modifier'),
         'fields': [{'name':'name', 'title':'Reference','dataType': 'TEXT', 'value': self['name']},
                 {'name':'description', 'title':'Description','dataType': 'TEXT', 'formType': 'textarea', 'value': self['description']},
                 {'name':'price', 'title':'Prix Hors Taxes','dataType': 'TEXT', 'value': self['price']},
                 {'name':'tax', 'title':'Valeur taxe (% du prix)','dataType': 'TEXT', 'value': self['tax']},
                 {'name':'shipping', 'title':'Frais de port','dataType': 'TEXT', 'value': self['shipping']},
                 ] }
    
    @KaraCos._Db.isaction
    def edit_storeitem(self,*args,**kw):
        """
         Modify properties of item
        """
        assert 'price' in kw
        kw['price'] = float(kw['price'])
        assert 'tax' in kw
        kw['tax'] = float(kw['tax'])
        assert 'shipping' in kw
        kw['shipping'] = float(kw['shipping'])
        self.update(kw)
        self.save()
    edit_storeitem.get_form = _edit_storeitem_form
    
    
    @KaraCos._Db.isaction
    def add_to_cart(self,*args,**kw):
        "Add item to ShoppingCart, with optional quantity, default is 1"
        
        person = self.__domain__._get_person_data()
        cart = self.__store__._get_active_cart_for_person(person)
        kw['item'] = self
        if 'number' not in kw:
            kw['number'] = 1
        else:
            if kw['number'] == "":
                kw['number'] = 1
            else:
                kw['number'] = int(kw['number'])
        cart._add_item(*args,**kw)
        return cart
    add_to_cart.form = {'title': _("Ajouter au panier"),
         'submit': _('Ajouter'),
         'fields': [{'name':'number', 'title':'Quantite','dataType': 'TEXT', 'value': 1}]}
        
        
    @KaraCos._Db.isaction
    def add_media(self,*args,**kw):
        ""
