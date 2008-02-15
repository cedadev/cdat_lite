"Error object for cdms module"
class CDMSError (Exception):
    def __init__ (self, args="Unspecified error from package cdms"):
        self.args=args
    def __str__(self):
        if isinstance(self.args,(list,tuple)):
            return ''.join(self.args)
        else:
            return self.args
