
import karacos

import paypal_express

def get_service(service):
    return eval("%s.Service" % service)
