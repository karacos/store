'''
Created on 15 dec. 2011

@author: nico
'''
import karacos
import math
class Service(karacos.apps['store'].providers.paybox.Service):
    
    def __init__(self,*args,**kw):
        """
        """
        self.log = karacos.core.log.getLogger(self)
        karacos.apps['store'].providers.paybox.Service.__init__(self,*args,**kw)
        self['_name'] = 'paybox'
        
    def do_forward(self,cart,payment):
        assert isinstance(cart, karacos.db['ShoppingCart'])
        assert isinstance(payment, karacos.db['Payment'])
        email_porteur = None
        if 'customer_mail' in cart:
            email_porteur = cart['customer_mail']
        else:
            email_porteur = karacos.serving.get_session().get_user_auth()._get_email()
        payment['service'] = {'name':self['_name']}
        bill = cart._get_bill_data()
        params = {}
        params['PBX_TOTAL'] = str(math.trunc(float(bill['total']) * 100)) # Total panier
        params['PBX_CMD'] = cart.id # Reference commande commercant
        params['PBX_DEVISE'] = "978" # default euro
        params['PBX_PORTEUR'] = email_porteur# email porteur de carte
        params['PBX_RETOUR'] = "montant:M;maref:R;auto:A;trans:T;pmt:P;carte:C;idtrans:S;pays:Y;erreur:E;validite:D;PPPS:U;IP:I;BIN6:N;digest:H;datrans:W;htrans:Q;sign:K"
        # variable (voir p19)
        params['PBX_SOURCE'] = "XHTML"
        params['PBX_REPONDRE_A'] = "http://%s%s/pay_callback/%s/srvcallback" % (cart.__store__.__domain__['fqdn'],
                                                                   cart.__store__._get_action_url(),
                                                                   payment.id) # callback url (in any case)
        params['PBX_IDENTIFIANT'] = "2" # identifiant paybox (default)
        params['PBX_EFFECTUE'] = "http://%s%s/pay_callback/%s/accept" % (cart.__store__.__domain__['fqdn'],
                                                                   cart.__store__._get_action_url(),
                                                                   payment.id) # url callback success
        params['PBX_REFUSE'] = "http://%s%s/pay_callback/%s/refuse" % (cart.__store__.__domain__['fqdn'],
                                                                   cart.__store__._get_action_url(),
                                                                   payment.id) # url callback refuse
        params['PBX_ANNULE'] = "http://%s%s/pay_callback/%s/cancel" % (cart.__store__.__domain__['fqdn'],
                                                                   cart.__store__._get_action_url(),
                                                                   payment.id) # url de callback annullation paiement
        # URL du serveur de paiement primaire de Paybox si
        #differente de celle par defaut :
        #version mobile :
        # https://tpeweb.paybox.com/cgi/ChoixPaiementMobile.cgi
        params['PBX_PAYBOX'] = 'https://tpeweb.paybox.com/cgi/ChoixPaiementMobile.cgi'
        params['PBX_BACKUP1'] = 'https://tpeweb1.paybox.com/cgi/ChoixPaiementMobile.cgi'
        params['PBX_BACKUP2'] = 'https://tpeweb2.paybox.com/cgi/ChoixPaiementMobile.cgi'
        params['PBX_BACKUP3'] = 'https://tpeweb3.paybox.com/cgi/ChoixPaiementMobile.cgi'
        payment['service']['do_forward'] = {
            "request": params,
            "response": self.call(params=params)
        }
        payment.save()
        pass

    def do_callback(self,payment,action,*args,**kw):
        """
            Actions parametres :
            - srvcallback - appel de paybox dans tous les cas
            - accept : url callback client via navigateur
            - refuse : url callback paiement refuse navigateur
            - cancel : url callback paiement annule navigateur
        dans le cas de srccallback, kw contient :
        montant : montant de la transaction
        maref : reference commande (cart.id)
        auto: numero d'autorisation
        trans: identifiant paybox service pour la transaction
        abonnement
        """
        if 'do_callback' not in payment['service']:
            payment['service']['do_callback'] = {}
        payment['service']['do_callback'][action] = kw
        payment.save()
        if action == 'cancel' or action == 'refuse':
            return payment.do_cancel()
        if action == 'accept':
            return payment.do_validate()
        if action == 'srvcallback':
            if kw['erreur'] == '00000' and 'auto' in kw:
                return payment.do_validate()
            else:
                return payment.do_cancel()