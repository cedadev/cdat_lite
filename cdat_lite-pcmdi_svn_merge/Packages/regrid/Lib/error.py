class RegridError (Exception):
    def __init__ (self, args="Unspecified error from regrid package"):
        self.args = args
    def __str__(self):
        return str(self.args)
    
