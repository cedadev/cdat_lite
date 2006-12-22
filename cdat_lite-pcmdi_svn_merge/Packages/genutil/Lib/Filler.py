class StringConstructor:
    """ This Class aims at spotting keyword in string and replacing them
    Usage
    Filler=StringConstructor(template)
    or
    Filler=StringConstructor()
    Filler.template=template

    template is a string of form
    template = 'my string here with %(keywords) in it'

    You can have has many 'keyword' as you want, and use them as many times as you want
    keywords are delimited on the left by %( and ) on the right
    
    In order to construct the string (i.e. replace keywrods with some values:

    str=Filler(keyword='kwstr')
    or
    Filler.keyword='kwstr'
    str=Filler()

    Example:
        structure='/pcmdi/amip/mo/%(variable)/%(model)/%(variable)_%(model).xml'
        Filler=StringConstructor(structure)
        Filler.variable='tas'
        myfilename=Filler.construct(structure,model='ugamp-98a')

        print myfilename # '/pcmdi/amip/mo/tas/ugamp-98a/tas_ugamp-98a.xml'
    
    """
    def __init__(self,template=None):
        self.template=template
    def construct(self,template=None,**kw):
        """
        construct, accepts a string with a unlimited number of keyword to replace
        keyword to replace must be in the format %(keyword) within the string
        keyword value are either passed as keyword to the construct function or preset
        Example:
        structure='/pcmdi/amip/mo/%(variable)/%(model)/%(variable)_%(model).xml'
        Filler=StringConstructor()
        Filler.variable='tas'
        myfilename=Filler.construct(structure,model='ugamp-98a')

        print myfilename
        """
        import string
        if template is None:
            template=self.template
##         # First sets all the keyword values passed
##         for k in kw.keys():
##             setattr(self,k,kw[k])
        # Now determine the keywords in the template:
        end=0
        s2=string.split(template,'%(')
        keys=[]
        for k in s2:
            sp=string.split(k,')')
            i=len(sp[0])
            if len(k)>i:
                if k[i]==')' and (not sp[0] in  keys):
                    keys.append(sp[0])
        
        # Now replace the keywords with their values
        for k in keys:
               template=string.replace(template,'%('+k+')',kw.get(k,getattr(self,k,'')))
##             cmd='template=string.replace(template,\'%('+k+')\',self.'+k+')'
##             exec(cmd)
        return template
    
    def __call__(self,*args,**kw):
        """default call is construct function"""
        return self.construct(*args,**kw)
    
Filler=StringConstructor()

if __name__=='__main__':
    Filler.variable='tas'
    structure='/pcmdi/amip/mo/%(variable)/%(model)/%(variable)_%(model).xml'
    myfilename=Filler.construct(structure,model='*')    
    print myfilename
