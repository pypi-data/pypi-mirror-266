'''
Class for working with Google via xmlriver service
'''

from .xmlriver import *

class Google(XmlRiver):
    url = 'http://xmlriver.com/search/xml'
    def __init__(self, user, key, **kwargs):
        self.user = user
        self.key = key
        super().__init__(user, key, **kwargs)
        print ()
    
    def get_cost(self):
        '''
        Get cost per 1 000 for Google
        '''
        return super().get_cost(type(self).__name__.lower())