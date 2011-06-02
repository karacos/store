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
        
    
    def _publish_node(self):
        karacos.db['WebNode']._publish_node(self)
        if 'get_store_folders' not in self['ACL']['group.everyone@%s' % self.__domain__['name']]:
            self['ACL']['group.everyone@%s' % self.__domain__['name']].append("get_store_folders")
        if 'get_items_list' not in self['ACL']['group.everyone@%s' % self.__domain__['name']]:
            self['ACL']['group.everyone@%s' % self.__domain__['name']].append("get_items_list")
        self['public'] = True
        self.save()
    
    @karacos._db.isaction
    def publish_node(self):
        self._publish_node()
        return {'status':'success', 'message':_("Le dossier est maintenant visible de tous"), 'success': True} 
    publish_node.label = _("Publier dossier boutique")
    
    def _is_public(self):    
        if 'public' not in self:
            self['public'] = False
            self.save()
        return self['public']
    
    def _unpublish_node(self):
        karacos.db['WebNode']._unpublish_node(self)
        self['public'] = False
        self.save()
    
    @karacos._db.isaction
    def unpublish_node(self):
        self._unpublish_node()
        return {'status':'success', 'message':_("Le dossier est maintenant ferme au public"), 'success': True} 
    publish_node.label = _("Publier dossier boutique")
    
    @karacos._db.isaction
    def create_store_folder(self,*args,**kw):
        return self._create_child_node(data=kw,type='StoreFolder')
    
    create_store_folder.form = {'title': _("Creer un dossier"),
         'submit': _('Creer'),
         'fields': [{'name':'name', 'title':'Nom','dataType': 'TEXT'},
                 {'name':'description', 'title':'Description','dataType': 'TEXT', 'formType': 'textarea'}
                 ] }
    
    @karacos._db.ViewsProcessor.isview('self', 'javascript')
    def __get_store_folders_by_id__(self,*args,**kw):
        """
        function(doc) {
        var label, auth;
            if (doc.parent_id === "%s" && doc.WebType === "StoreFolder" && !("_deleted" in doc && doc._deleted == true)) {
                for (auth in doc.ACL) {
                    if (doc.ACL[auth].join().search(/w_browse/) != -1) {
                        if (doc.label) {
                            label = doc.label;
                        } else {
                            label = doc.name;
                        }
                        emit(auth,{name: doc.name, label: label});
                    }
                }
            }
        }
        """
    
    def _get_store_folders_by_id_(self):
        """
        """
        user = self.__domain__.get_user_auth()
        cart = self.get_open_cart_for_user()
        keys = [] + user['groups']
        keys.append("user.%s" % user['name'])
        results = self.__get_store_folders_by_id__(*(), **{'keys':keys})
        result = {'success': True, 
                      'status': 'success',
                      'data': [],
                      'total': 0
                      }
        ids = []
        for item in results:
            if item.id not in ids:
                result['data'].append({'id': item.id,'name': item.value['name'],'label': item.value['label']})
                ids.append(item.id)
        total = len(results)
        return result
    
    @karacos._db.isaction
    def get_store_folders(self):
        return self._get_store_folders_by_id_()
    
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
    
    @karacos._db.ViewsProcessor.isview('self', 'javascript')
    def _get_items_by_auth_(self,*args,**kw):
        """
        function(doc) {
            if (doc.public_price !== undefined && doc.parent_id == "%s" && !("_deleted" in doc && doc._deleted == true)) {
                for (var auth in doc.ACL) {
                    if (doc.ACL[auth].join().search(/w_browse/) != -1) {
                        emit(auth,doc);
                    }
                }
            }
        }
        """
    @karacos._db.isaction
    def get_items_list(self, count=None, page=None):
        count = int(count)
        page = int(page)
        return self._get_items_list(self._get_items_by_auth_,count,page)
    
    def _get_items_list(self,view, count, page):
        ""
        user = self.__domain__.get_user_auth()
        cart = self.__store__.get_open_cart_for_user()
        keys = [] + user['groups']
        keys.append("user.%s" % user['name'])
        results = view(*(), **{'keys':keys})
        result = {'success': True, 
                      'status': 'success',
                      'data': [],
                      'total': 0,
                      'page_total': 0
                      }
        min = (page - 1) * count
        max = page * count
        current = 0
        self.log.error("_get_items_list: results : %s" % results)
        items_id = []
        for item in results:
            if item.id not in items_id: # Prevent multiple entries
                items_id.append(item.id)
                if min <= current and current < max:
                    dbitem = self.db[item.id]
                    image = ''
                    if 'main_pic' in item.value:
                        image = "/_atts/%s/%s" % (item.id,item.value['main_pic'])
                    elif 'k_atts' in item.value:
                        for file in item.value['k_atts']:
                            if item.value['k_atts'][file]['type'].startswith('image') and image == '':
                                image = "/_atts/%s/%s" % (item.id,file)
                    price = 0
                    if 'public_price' in item.value:
                        price = item.value['public_price']
                    if price == None or price == "":
                        price = 0
                    price = "%.2f" % float(price)
                    if 'content' in item.value and 'title' in item.value:
                        description = ""
                        if 'description' not in item.value:
                            description = item.value['content']
                        else:
                            description = item.value['description']
                        number = 0
                        if item.id in cart['items']:
                            number = cart['items'][item.id]
                        result['data'].append({'id': item.id,
                                               'name': item.value['name'],
                                               'url': dbitem._get_action_url(),
                                               'store_url': self.__store__._get_action_url(),
                                               'description': description,
                                               'image': image,
                                               'price': price,
                                               'number': number,
                                               'title': item.value['title']
                                               })
                current = current + 1
        result['total'] = current
        result['page_total'] = current / count
        if current % count != 0:
            result['page_total'] = result['page_total'] +1 
        return result