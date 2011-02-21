'''
Created on 13 janv. 2010

@author: nico
'''


'''
Created on 13 janv. 2010

@author: nico
'''

__author__="Nicolas Karageuzian"
__contributors__ = []

import sys
import karacos

class StoreItem(karacos.db['Resource']):
    '''
    Basic resource
    '''    
    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent,karacos.db['StoreParent'])
        assert 'WebType' in data, "Could not instanciate abstract type StoreItem"
        return karacos.db['Resource'].create(parent=parent,base=False,data=data)

    def __init__(self,parent=None,base=None,data=None,domain=None):
        assert isinstance(parent,karacos.db['StoreParent'])        
        karacos.db['Resource'].__init__(self,parent=parent,base=base,data=data)
        self.__store__ = parent.__store__
        selfsave = False
        if 'public_price' not in data:
            self['public_price'] = None
            selfsave = True
        if 'store_id' not in self:
            self['store_id'] = self.__store__.id
            selfsave = True
        if selfsave:
            self.save()
    
    def _publish_node(self):
        karacos.db['Resource']._publish_node(self)
        self['ACL']['group.everyone@%s' % self.__domain__['name']].append("add_to_cart")
        self.save()
    
    @karacos._db.isaction
    def publish_node(self):
        self._publish_node()
        return {'status':'success', 'message':_("L'Article est maintenant visible de tous")}
    
    def _edit_storeitem_form(self):
        if 'content' not in self:
            self['content'] = ''
        if 'tax' not in self:
            self['tax'] = 0
        if 'public_price' not in self:
            self['public_price'] = 0
        self.save()
        return {'title': _("Modifier le produit"),
         'submit': _('Modifier'),
         'fields': [{'name':'Title', 'title':'Title','dataType': 'TEXT', 'value': self['name']},
                 {'name':'content', 'title':'Description','dataType': 'TEXT', 'formType': 'WYSIWYG', 'value': self['content']},
                 {'name':'public_price', 'title':'Prix Hors Taxes','dataType': 'TEXT', 'value': self['public_price']},
                 {'name':'tax', 'title':'Valeur taxe (% du prix)','dataType': 'TEXT', 'value': self['tax']}
                 ] }
    
    @karacos._db.isaction
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
    
    
    def _do_add_validation(self,cart,number):
        """
        When item is added to cart, process custom validation (abstract)
        """
        assert False, "Method _do_add_validation has to be implemented in subclass"

    

    def _add_to_cart(self,*args,**kw):
        "Add item to ShoppingCart, with optional quantity, default is 1"
        cart = self.__store__.get_open_cart_for_user()
        
        kw['item'] = self
        if 'number' not in kw:
            kw['number'] = 1
        else:
            if kw['number'] == "":
                kw['number'] = 1
            else:
                kw['number'] = int(kw['number'])
        self._do_add_validation(cart,kw['number'])
        cart._add_item(*args,**kw)
        return cart

    @karacos._db.isaction
    def add_to_cart(self,*args,**kw):
        return {'success': True, 'status': 'success', 'message': _("Item added to cart"), 'data':self._add_to_cart(*args,**kw)}
    add_to_cart.form = {'title': _("Ajouter au panier"),
         'submit': _('Ajouter'),
         'fields': [{'name':'number', 'title':'Quantite','dataType': 'TEXT', 'value': 1}]}
    add_to_cart.label = _("Ajouter au panier")
        
        
    @karacos._db.isaction
    def add_media(self,*args,**kw):
        """
        """
    
    def _do_cart_validation(self,cart):
        """
        While cart validation, tells if this item has to be shipped (or other requirement, implemented in type itself)
        """
        assert False, "Method _do_cart_validation has to be implemented in subclass"
    
    def _do_cart_processing(self,cart):
        """
        When item is sold and payment validated
        """
        assert False, "Method _do_cart_processing has to be implemented in subclass"
    
    def _do_cart_cancel(self,cart):
        """
        When payment fails
        """
        assert False, "Method _do_cart_cancel has to be implemented in subclass"