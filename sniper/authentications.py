class BaseAuthentication:
    def __init__(self, controller):
        self.controller = controller

    def authenticate(self, request):
        '''
            return None or an object.
        '''
        pass
