'''
Created on 13 janv. 2010

@author: nico
'''
import sys
import core
import providers
import KaraCos
#import services


class Root():
    
    def __init__(self):
        try:
            KaraCos.Apps['store'].services = __import__("services", globals(), locals(), ['all'], -1)
        except:
            KaraCos._Db.log.log_exc(sys.exc_info(),"error")