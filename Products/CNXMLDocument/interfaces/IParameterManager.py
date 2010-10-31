from zope.interface import Interface

class IParameterManager(Interface):
    """
    Manages stylesheet parameters (much like Zope Properties)
    """

    def getParameters():
        """
        Return a dictinary of the associated stylesheet parameters
        """

    def manage_addParameter(key='',value='',type='',REQUEST=None):
        """Add a new parameter via the web"""

    def manage_delParameters(keys=None,REQUEST=None):
        """Delete the specified parameter(s) via the web"""

    def manage_editParameters(values=None,REQUEST=None):
        """Edit the specified parameter(s) via the web"""
    
