
import karacos

import paypal_express
import paybox

def get_service(service):
    return eval("%s.Service" % service)
