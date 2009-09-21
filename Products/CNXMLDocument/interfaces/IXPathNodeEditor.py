from Interface import Interface

################################################################
# IXPathNodeEditor Interface
################################################################

class IXPathNodeEditor(Interface):
    """
    Provides the ability to manipulate an XML document via XPath.

    In all of these methods, it is assumed that the provided XPath
    expressions refers to a single element node.  If the XPath refers
    to a nodeset, the first node will be used.  It is an error if the
    XPath refers to a non-element node
    """

    def xpathReplaceTree(xpath, xmlText):
        """
        Find the node specific by xpath and replace it and its children with the provided subtree.
        """

    def xpathDeleteTree(self, xpath):
        """
        Find the node specified by xpath and delete it along with all its children.
        """

    def xpathInsertTree(self, xpath, xmlText):
        """
        Insert the provided xmlText as a new subtree immediately preceeding the specified node.
        """        

    def xpathAppendTree(self, xpath, xmlText):
        """
        Append the provided xmlText as a new subtree immediately following the specified node.
        """        

