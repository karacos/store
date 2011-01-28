'''
Created on 1 juin 2010

@author: nico
'''


__author__ = "Nicolas Karageuzian"
__contributors__ = []

import karacos

class HardItem(karacos.db['StoreItem']):
    '''
    Container for Store items as a piece of hard, material part or stuff
    '''

    def __init__(self,parent=None,base=None,data=None):
        karacos.db['StoreItem'].__init__(self,parent=parent,base=base,data=data)
        self.__bo_node__ = self.__store__._get_backoffice_node()
    
    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(data,dict)
        assert isinstance(parent,karacos.db['StoreParent'])
        if 'WebType' not in data:
            data['WebType'] = 'HardItem'
        if 'buy_cost' in data:
            data['buy_cost'] = int(data['buy_cost'])
        if 'min_sell_price' in data:
            data['min_sell_price'] = int(data['min_sell_price'])
        if 'min_sell_price' in data:
            data['min_sell_price'] = int(data['min_sell_price'])
        if 'public_price' in data:
            data['public_price'] = int(data['public_price'])
        if 'tax' in data:
            data['tax'] = int(data['tax'])
        if 'stock' in data:
            data['stock'] = int(data['stock'])
        result = karacos.db['StoreItem'].create(parent=parent,base=base,data=data)

        return result
    
    def _get_stock(self):
        return self['stock']
    
    @karacos._db.isaction
    def edit_item(self,title=None,content=None,buy_cost=None, min_sell_price=None, public_price=None, tax=None, stock=None):
        ""
        self['title'] = title
        self['content'] = content
        self['buy_cost'] = int(buy_cost)
        self['min_sell_price'] = int(min_sell_price)
        self['public_price'] = int(public_price)
        self['tax'] = int(tax)
        self['stock'] = int(stock)
        self.save()
        
        return {'status': 'success', 'success': True, 'message': "Item updated"}
    
    def _get_edit_item_form_(self):
        if 'title' not in self:
            self['title'] = ""
        if 'content' not in self:
            self['content'] = ""
        if 'buy_cost' not in self:
            self['buy_cost'] = 0
        if 'min_sell_price' not in self:
            self['min_sell_price'] = 0
        if 'public_price' not in self:
            self['public_price'] = 0
        if 'tax' not in self:
            self['tax'] = 0
        if 'stock' not in self:
            self['stock'] = 0
        return {'title': _("Modifier le produit"),
         'submit': _('Modifier'),
         'fields': [{'name':'name', 'title':'Reference','dataType': 'TEXT', 'value': self['name']},
                    {'name':'title', 'title':'Title','dataType': 'TEXT', 'value': self['title']},
                 {'name':'content', 'title':'Description','dataType': 'TEXT', 'formType': 'WYSIWYG', 'value': self['content']},
                 {'name':'public_price', 'title':'Prix Hors Taxes','dataType': 'TEXT', 'value': self['public_price']},
                 {'name':'min_sell_price', 'title':'Prix Mini Hors Taxes','dataType': 'TEXT', 'value': self['min_sell_price']},
                 {'name':'buy_cost', 'title':'Prix Mini Hors Taxes','dataType': 'TEXT', 'value': self['buy_cost']},
                 {'name':'stock', 'title':'Prix Mini Hors Taxes','dataType': 'TEXT', 'value': self['stock']},
                 {'name':'tax', 'title':'Valeur taxe (% du prix)','dataType': 'TEXT', 'value': self['tax']}
                 ] }
    edit_item.label = _("Modifier le produit")
    edit_item.get_form = _get_edit_item_form_
    
    @karacos._db.isaction
    def add_stock(self,numbervalue='0'):
        number = int(numbervalue)
        self['stock'] = self['stock'] + number
        self.save()
        return {'status':'success','success': True,
                'message':"Stock added, new stock : %s "% self['stock']}
    
    def _do_add_validation(self,cart,number):
        """
        """
        assert number <= self['stock'], _("Stock insuffisant")
    
    def _do_cart_validation(self,cart):
        """
        before payement
        such an item requires shipping adress
        """
        if 'shipping_adr' not in cart:
            raise karacos.http.DataRequired("Validate shipping","","/%s?method=validate_cart"%self.__store__.get_relative_uri(),self.__store__,self.__store__.add_cart_shipping)
        # Number of this item odered
        #cart_number = cart['items'][self.id]
        self.__bo_node__._reserve_item(self, cart)
    
    def _do_cart_processing(self,cart):
        """
        When cart is payed
        """
        self.__bo_node__._reserved_payed(self, cart)
        
    def _do_cart_cancel(self,cart):
        """
        When cart is cancelled, or payement failure
        """
        self.__bo_node__._reserved_cancel(self, cart)