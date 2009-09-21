from Interface import Interface

################################################################
# IXMLFile Interface
################################################################

class IXMLFile(Interface):
    """
    Basic XML interface, incuding validation and transformation
    """

    def validate():
        """
        Returns text representing validation errors, or None upon success
        """

    def transform(ns, stylesheet=None, **params):
        """
        Transform the XML file with the supplied stylesheet (or an
        appropriate default based on the provided target namespaces)

        - ns: list of target XML namespaces

        - stylesheet: string with filename of stylesheet to use for transformation

        - params: dictionary of stylesheet parameters
        """

    def normalize():
        """
        Return 'normalized' document with entities expanded, etc.
        """

    def getSource():
        """
        Return the full XML Document source
        """

    def setSource(source):
        """
        Set the document source
        """
        
    def getDoctype():
        """
        Return the PUBLIC doctype identifier
        """

    def setDoctype(system, public=None):
        """
        Set the DOCTYPE identifiers
        """
