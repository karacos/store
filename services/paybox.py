'''
Created on 15 dec. 2011

@author: nico
'''
import karacos
import re, math

script_errors = {
                "-1" : "Erreur de transmission",
                "-2" : "Erreur memoire",
                "-3" : "Erreur de lecture des parametres",
                "-4" : "Erreur parametre trop long",
                "-5" : "Erreur ouverture de fichier",
                "-6" : "Erreur fichier incorrect",
                "-7" : "Erreur information obligatoire manqualte",
                "-8" : "Erreur texte dans donnee numerique",
                "-9" : "Erreur CODE SITE non valide (len !=7)",
                "-10": "Erreur CODE RANG non valide (len != 2)",
                "-11": "Erreur len TOTAL > 11 ou < 3",
                "-12": "Erreur len LAN/DEVISE != 3",
                "-13": "Erreur CMD vide ou trop long",
                "-14": "Erreur NA",
                "-15": "Erreur NA",
                "-16": "Erreur ADRESSE PORTEUR invalide",
                "-17": "Erreur de coherence multi-paniers",
                "-18": "Erreur faille XSS dans la page d'appel",
                "-19": "Erreur non documente",
                "-20": "Erreur carte cadeau",
                "-21": "Erreur valeur variable > valeur max"
            }

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
        params['PBX_RETOUR'] = 'montant:M;maref:R;auto:A;trans:T;pmt:P;carte:C;idtrans:S;pays:Y;erreur:E;validite:D;PPPS:U;IP:I;BIN6:N;digest:H;datrans:W;htrans:Q;sign:K'
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
        params['PBX_ERREUR'] = "http://%s%s/pay_callback/%s/erreur" % (cart.__store__.__domain__['fqdn'],
                                                                   cart.__store__._get_action_url(),
                                                                   payment.id)
        # URL du serveur de paiement primaire de Paybox si
        #differente de celle par defaut :
        #version mobile :
        # https://tpeweb.paybox.com/cgi/ChoixPaiementMobile.cgi
        params['PBX_PAYBOX'] = 'https://tpeweb.paybox.com/cgi/ChoixPaiementMobile.cgi'
        params['PBX_BACKUP1'] = 'https://tpeweb1.paybox.com/cgi/ChoixPaiementMobile.cgi'
        params['PBX_BACKUP2'] = 'https://tpeweb2.paybox.com/cgi/ChoixPaiementMobile.cgi'
        params['PBX_BACKUP3'] = 'https://tpeweb3.paybox.com/cgi/ChoixPaiementMobile.cgi'
        payment['service']['do_forward'] =  self.call(params=params)
        payment.save()
        if payment['service']['do_forward']['retcode'] != 0:
            for line in payment['service']['do_forward']['stdout'].splitlines():
                url = re.match('<META HTTP-EQUIV="refresh" CONTENT="0;URL=(http://.*)">',line, 0)
                if url != None:
                    payment['service']['do_forward']['url_err'] = url.groups()[0]
                    payment.save()
                    return {"success": False, "message": "Payment preparation failed", "data": {"service": "paybox", "id": payment.id, "errurl": payment['service']['do_forward']['url_err']}}
        if payment['service']['do_forward']['stdout'].find("AUCUN SERVEUR DISPONIBLE") != -1:
            return {"success": False, "message": "Serveur de paiement indisponible", "data":{"do_cancel": payment.do_cancel(),"id": payment.id,"service": "paybox"}}
        if re.match("^[a-zA-Z0-9]*$", payment['service']['do_forward']['stdout'], 0) == None:
            return {"success": False, "message": "DataString invalid", "data":{"do_cancel": payment.do_cancel(),"id": payment.id,"service": "paybox"}}
        params['PBX_DATA'] = payment['service']['do_forward']['stdout'].splitlines()[0]
        return {"success": True, "data":{"id": payment.id, "service": "paybox", "target_url": self.__conf__['target_url'], "method": "POST", "params": params}}
        

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
            # See spec p19
            # TODO: strict imperative verifications
            if kw['erreur'] == '00000' and 'auto' in kw:
                return ""#  - should return empty html
            else:
                return payment.do_cancel()
        if action == 'erreur':
            assert 'NUMERR' in kw
            
            payment['cancel_reason']= { 'message': script_errors[kw['NUMERR']], 'errCode': kw['NUMERR']}
            payment.save()
            return {'success': False, 'cancel': payment.do_cancel(), 'message': script_errors[kw['NUMERR']], 'errCode': kw['NUMERR']}          