'''
Created on 13 janv. 2010

@author: nico
'''
from uuid import uuid4
import simplejson as json
import KaraCos

class ShoppingCart(KaraCos.Db.Node):
    '''
    Basic resource
    '''


    def __init__(self,parent=None,base=None,data=None):
        KaraCos.Db.Node.__init__(self,parent=parent,base=base,data=data)
        self.parent = parent
        self.__store__ = parent
        if 'items' not in self:
            self['items'] = {}
        self.save()

    @staticmethod
    def create(parent=None, base=None,data=None,owner=None):
        assert isinstance(parent,KaraCos.Db.Store), "Parent type invalid : %s - Should be Store" % type(parent)
        assert isinstance(data,dict)
        if 'type' not in data:
            data['type'] = 'ShoppingCart'
        result = KaraCos.Db.Node.create(parent=parent,base=base,data=data,owner=owner)
        return result
    
    def _add_item(self,*args,**kw):
        assert 'number' in kw
        assert 'item' in kw
        assert isinstance(kw['item'],KaraCos.Db.StoreItem)
        if kw['item'].id not in self['items']:
            self['items'][kw['item'].id] = kw['number']
        else:
            self['items'][kw['item'].id] = self['items'][kw['item'].id] + kw['number']
        self.save()
    
    @KaraCos._Db.ViewsProcessor.isview('self','javascript')
    def __get_items_array__(self,items):
        """
        function(doc) {
            parent_id = "%s"
            items = %s
            for (var i=0; i<= items.length; i++)
                if (doc._id == items[i])
                    emit(doc._id, doc)
        }
        """
     
    def _get_bill_data(self):
        result = {'items':{},'total':0, 'net_total':0, 'tax_total':0}
        for item in self.__get_items_array__(json.dumps(self['items'].keys())):
            result['items'][item.key] = {'name':item.value['name'],
                                            'tax':item.value['tax'],
                                            'price':item.value['price'],
                                            'number':self['items'][item.key],
                                            'total': item.value['price'] * self['items'][item.key],
                                            'tax_total': item.value['tax'] * item.value['price'] * self['items'][item.key],
                                            'net_total': (item.value['price'] + item.value['tax'] * item.value['price']) * self['items'][item.key]}
            result['total'] = result['total'] + result['items'][item.key]['total']
            result['tax_total'] = result['tax_total'] + result['items'][item.key]['tax_total']
            result['net_total'] = result['net_total'] + result['items'][item.key]['net_total']
        return result
    
    def _add_shipping_adress(self,adress):
        ""
    def __get_active_payment__(self):
        """
        function(doc){
         if(doc.parent_id == "%s" && doc.status == "active")
             emit(doc._id,doc)
        }
        """
        
    def _get_active_payment(self):
        """
        """
        result = None
        payments = self.__get_active_payment__()
        assert payments.__len__() <= 1, "payments : More than one active payments for Cart"
        if payments.__len__() == 1:
            for payment in payments:
#                    KaraCos._Db.log.debug("get_child_by_name : db.key = %s db.value = %s" % (child.key,domain.value) )
                result = self.db[payments.key]
        else:
            return None
    
        return result
    
    def _has_active_payment(self):
        """
        """
        return False
    
    def _create_payment(self,service):
        """
        service : name of the service : 'papal'
        """
        assert not self._has_active_payment()
        name = "%s" % uuid4().hex
        data = {'name':name,'service':service['_name'] ,'status':'active'}
        self._create_child_node(data=data,type='Payment')
        return self.__childrens__[name]
        
        
    def _cancel_payment(self):
        ""
        
    