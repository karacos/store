"""
Fournisseurs de services utiles pour l'exposition d'un store, aide au referencement des articles.
Wrapper d'appel a ces services (ESB like)
"""

import karacos

import paypal, paybox

_available_providers = ["paypal"]


class Provider():
    
    def __init__(self,*args,**kw):
        assert 'provider_name' in kw
        assert kw['provider_name'] in _available_providers, _("Unknow service provider : %s" % kw['provider_name'])
        self.__provider_type__ = eval("%s.Service",kw['provider_name'])
    
    def is_ready(self):
        ""
        try:
            assert '__provider_instance__' in self.__dict__
            return True
        except:
            return False
    
    def call_service(self,*args,**kw):
        ""
        assert self.is_ready(), _("Provider not ready, please configure")
        assert 'uri' in kw
        assert 'params' in kw