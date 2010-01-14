# Load fixture

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import libxml2
import libxslt
from BaseTestCase import BaseTestCase
from Products.CNXMLDocument import XMLService

noNS = "<tag>Hello</tag>"
cnxml = "<para xmlns='http://cnx.rice.edu/cnxml' id='hello'>Hello</para>"
cnxml_mathml = "<para xmlns='http://cnx.rice.edu/cnxml' xmlns:m='http://www.w3.org/1998/Math/MathML' id='hello'>Hello</para>"
cnxml_mathml2 = "<para xmlns='http://cnx.rice.edu/cnxml' xmlns:m='http://www.w3.org/1998/Math/MathML' id='hello'>Hello<m:math><m:cn>0</m:cn></m:math></para>"
nested_cnxml = "<section id='s1' xmlns='http://cnx.rice.edu/cnxml'><para id='hello'>Hello</para></section>"

cnxml_dtd = \
"""<?xml version='1.0'?>
<!DOCTYPE para PUBLIC "-//CNX//DTD CNXML 0.5//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_plain.dtd">
<para xmlns="http://cnx.rice.edu/cnxml" id="hello">Hello</para>
"""

cnxml_mathml_dtd = \
"""<?xml version='1.0'?>
<!DOCTYPE para PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<para xmlns="http://cnx.rice.edu/cnxml" xmlns:m='http://www.w3.org/1998/Math/MathML' id="hello">Hello<m:math><m:cn>0</m:cn></m:math></para>
"""


class ParseDoc(BaseTestCase):
    """
    Test the parseDoc() method
    """

    def testParseBadDocument(self):
        """parseDoc() must fail if the document cannot be parsed"""
        self.assertRaises(XMLService.XMLError, XMLService.parseDoc, 'non-XML')

    def testParseDocumentReturnsXMLDoc(self):
        """parseDoc must return an xmlDoc"""
        doc = XMLService.parseDoc(noNS)
        self.failUnless(isinstance(doc, libxml2.xmlDoc))
        doc.freeDoc()

    def testParseDocument(self):
        """return of parseDoc must serializes correctly"""
        doc = XMLService.parseDoc(noNS)
        self.assertEquals(doc.serialize(), '<?xml version="1.0"?>\n<tag>Hello</tag>\n')
        doc.freeDoc()


class XsltPipeline(BaseTestCase):
    """
    Test the xsltPipeline() method
    """

    def testEmptyPipeline(self):
        """xsltPipeline must serialize original doc if pipeline is empty"""
        doc = XMLService.parseDoc(noNS)
        self.assertEquals(XMLService.xsltPipeline(doc, []), '<?xml version="1.0"?>\n<tag>Hello</tag>\n')
        doc.freeDoc()

    def testSingleTransform(self):
        """xsltPipeline must correctly perform single transform"""
        doc = XMLService.parseDoc(noNS)
        self.assertEquals(XMLService.xsltPipeline(doc, ['test.xsl']), 'Success')
        doc.freeDoc()

    def testDoubleTransform(self):
        """xsltPipeline must correctly perform double transform"""
        doc = XMLService.parseDoc(noNS)
        self.assertEquals(XMLService.xsltPipeline(doc, ['step1.xsl', 'step2.xsl']), 'Success')
        doc.freeDoc()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    #suite.addTest(makeSuite(ParseDoc))
    suite.addTest(makeSuite(XsltPipeline))
    return suite

if __name__ == '__main__':
    framework()
