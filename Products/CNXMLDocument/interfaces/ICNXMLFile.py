from IXMLFile import IXMLFile

class ICNXMLFile(IXMLFile):
    """Customized XML file for CNXML language"""

    def createTemplate(namespaces, **kw):
        """
        Create a blank document based on the template matching the
        specified namespaces.  The optional keyword arguments may
        provide data for the template
        """

    def getContent():
        """
        Get the content (non-metadata) portion of the document
        """

    def setContent(content):
        """
        Set the content (non-metadata) portion of the document
        """

    def getMetadata():
        """
        Get the metadata portion of the document
        """

    def setMetadata(metadata):
        """
        Set the metadata of the CNXML document

        - metadata: dictionary of metadata keys, values
        """

    def clearMetadata():
        """
        Remove the metadata segment of the CNXML document
        """

    def setTitle(title):
        """
        Set the title of the document
        """

    def getTitle():
        """
        Get the title of the document
        """


