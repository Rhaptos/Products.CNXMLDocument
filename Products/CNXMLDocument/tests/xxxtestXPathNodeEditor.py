# Load fixture

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from BaseTestCase import BaseTestCase
from Products.CNXMLDocument.CNXMLFile import CNXMLFile, XPathError, CNXMLFileError

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


class XPathNodeEditorInterface(BaseTestCase):
    """
    Unit tests for CNXMLFile.  Ensure that CNXMLFile correctly
    implements IXPathNodeEditor.
    """
    
    def testImplementsIXPathNodeEditor(self):
        """CNXMLFile must implement IXPathNodeEditor"""
        from Products.CNXMLDocument.interfaces.IXPathNodeEditor import IXPathNodeEditor
        self.failUnless(IXPathNodeEditor.isImplementedByInstancesOf(CNXMLFile))


class XPathInsertTree(BaseTestCase):
    """
    Test the xpathInsertTree() method
    """

    def testInsertTreeBadDocument(self):
        """xpathInsertTree() must fail if the document cannot be parsed"""
        self.doc.setSource('non-XML')
        self.assertRaises(CNXMLFileError, self.doc.xpathInsertTree, "/cnx:document/cnx:content/cnx:para", cnxml)

    def testInsertTreeInvalidXPath(self):
        """xpathInsertTree() must raise XPathError for an invalid xpath"""
        self.assertRaises(XPathError, self.doc.xpathInsertTree, "::", cnxml)

    def testInsertTreeBadXPath(self):
        """xpathInsertTree() must raise XPathError for a bad xpath"""
        self.assertRaises(XPathError, self.doc.xpathInsertTree, "//cnx:para[2]", cnxml)

    def testInsertTreeNoText(self):
        """xpathInsertTree() must raise ValueError if non-XML provided"""
        self.assertRaises(ValueError, self.doc.xpathInsertTree, "/cnx:document/cnx:content/cnx:para", "")

    def testInsertNoNS(self):
        """xpathInsertTree() should put a tree with namespace into the default namespace"""
        self.doc.xpathInsertTree("/cnx:document/cnx:content/cnx:para", noNS)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <tag>Hello</tag><para id="world">World</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testInsertCNXML(self):
        """xpathInsertTree() should correctly insert a CNXML tree"""
        self.doc.xpathInsertTree("/cnx:document/cnx:content/cnx:para", cnxml)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="hello">Hello</para><para id="world">World</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testInsertCNXMLMathML(self):
        """xpathInsertTree() should correctly insert a cnxml tree with an additional namespace declaration"""
        self.doc.xpathInsertTree("/cnx:document/cnx:content/cnx:para", cnxml_mathml)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="hello">Hello</para><para id="world">World</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testInsertCNXMLMathML2(self):
        """xpathInsertTree() should correctly insert a subtree with both CNXML and MathML"""
        self.doc.xpathInsertTree("/cnx:document/cnx:content/cnx:para", cnxml_mathml2)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="hello">Hello<m:math><m:cn>0</m:cn></m:math></para><para id="world">World</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testInsertNestedCNXML(self):
        """xpathInsertTree() should correctly insert a subtree with nested CNXML"""
        self.doc.xpathInsertTree("/cnx:document/cnx:content/cnx:para", nested_cnxml)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <section id="s1"><para id="hello">Hello</para></section><para id="world">World</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testInsertCNXMLDTD(self):
        """xpathInsertTree() should correctly insert a subtree with CNXML that includes a DTD"""
        self.doc.xpathInsertTree("/cnx:document/cnx:content/cnx:para", cnxml_dtd)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="hello">Hello</para><para id="world">World</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testInsertCNXMLMathMLDTD(self):
        """xpathInsertTree() should correctly insert a subtree with CNXML that includes the MathML DTD"""
        self.doc.xpathInsertTree("/cnx:document/cnx:content/cnx:para", cnxml_mathml_dtd)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="hello">Hello<m:math><m:cn>0</m:cn></m:math></para><para id="world">World</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)


class XPathAppendTree(BaseTestCase):
    """
    Test the xpathAppendTree() method
    """

    def testAppendTreeBadDocument(self):
        """xpathAppendTree() must fail if the document cannot be parsed"""
        self.doc.setSource('non-XML')
        self.assertRaises(CNXMLFileError, self.doc.xpathAppendTree, "/cnx:document/cnx:content/cnx:para", cnxml)

    def testAppendTreeInvalidXPath(self):
        """xpathAppendTree() must raise XPathError for an invalid xpath"""
        self.assertRaises(XPathError, self.doc.xpathAppendTree, "::", cnxml)

    def testAppendTreeBadXPath(self):
        """xpathAppendTree() must raise XPathError for a bad xpath"""
        self.assertRaises(XPathError, self.doc.xpathAppendTree, "//cnx:para[2]", cnxml)

    def testAppendTreeNoText(self):
        """xpathAppendTree() must raise ValueError if non-XML provided"""
        self.assertRaises(ValueError, self.doc.xpathAppendTree, "/cnx:document/cnx:content/cnx:para", "")

    def testAppendNoNS(self):
        """xpathAppendTree() should put a tree with namespace into the default namespace"""
        self.doc.xpathAppendTree("/cnx:document/cnx:content/cnx:para", noNS)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="world">World</para><tag>Hello</tag>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testAppendCNXML(self):
        """xpathAppendTree() should correctly append a CNXML tree"""
        self.doc.xpathAppendTree("/cnx:document/cnx:content/cnx:para", cnxml)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="world">World</para><para id="hello">Hello</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testAppendCNXMLMathML(self):
        """xpathAppendTree() should correctly append a cnxml tree with an additional namespace declaration"""
        self.doc.xpathAppendTree("/cnx:document/cnx:content/cnx:para", cnxml_mathml)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="world">World</para><para id="hello">Hello</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testAppendCNXMLMathML2(self):
        """xpathAppendTree() should correctly append a subtree with both CNXML and MathML"""
        self.doc.xpathAppendTree("/cnx:document/cnx:content/cnx:para", cnxml_mathml2)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="world">World</para><para id="hello">Hello<m:math><m:cn>0</m:cn></m:math></para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testAppendNestedCNXML(self):
        """xpathAppendTree() should correctly append a subtree with nested CNXML"""
        self.doc.xpathAppendTree("/cnx:document/cnx:content/cnx:para", nested_cnxml)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="world">World</para><section id="s1"><para id="hello">Hello</para></section>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testAppendCNXMLDTD(self):
        """xpathAppendTree() should correctly append a subtree with CNXML that includes a DTD"""
        self.doc.xpathAppendTree("/cnx:document/cnx:content/cnx:para", cnxml_dtd)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="world">World</para><para id="hello">Hello</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testAppendCNXMLMathMLDTD(self):
        """xpathAppendTree() should correctly append a subtree with CNXML that includes the MathML DTD"""
        self.doc.xpathAppendTree("/cnx:document/cnx:content/cnx:para", cnxml_mathml_dtd)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="world">World</para><para id="hello">Hello<m:math><m:cn>0</m:cn></m:math></para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

class XPathDeleteTree(BaseTestCase):
    """
    Test xpathDeleteTree() functionality.
    """

    def testDeleteTreeBadDocument(self):
        """xpathDeleteTree() must fail if the document cannot be parsed"""
        self.doc.setSource('non-XML')
        self.assertRaises(CNXMLFileError, self.doc.xpathDeleteTree, "/cnx:document/cnx:content/cnx:para")

    def testDeleteTreeInvalidXPath(self):
        """xpathDeleteTree() must raise XPathError for an invalid xpath"""
        self.assertRaises(XPathError, self.doc.xpathDeleteTree, "::")

    def testDeleteTreeBadXPath(self):
        """xpathDeleteTree() must raise XPathError for a bad xpath"""
        self.assertRaises(XPathError, self.doc.xpathDeleteTree, "//cnx:para[2]")

    def testDeleteCNXML(self):
        """xpathDeleteTree() should correctly delete a CNXML node"""
        self.doc.xpathDeleteTree("/cnx:document/cnx:content/cnx:para")

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

class XPathReplaceTree(BaseTestCase):
    """
    Test the xpathReplaceTree() method
    """

    def testReplaceTreeBadDocument(self):
        """xpathReplaceTree() must fail if the document cannot be parsed"""
        self.doc.setSource('non-XML')
        self.assertRaises(CNXMLFileError, self.doc.xpathReplaceTree, "/cnx:document/cnx:content/cnx:para", cnxml)

    def testReplaceTreeInvalidXPath(self):
        """xpathReplaceTree() must raise XPathError for an invalid xpath"""
        self.assertRaises(XPathError, self.doc.xpathReplaceTree, "::", cnxml)

    def testReplaceTreeBadXPath(self):
        """xpathReplaceTree() must raise XPathError for a bad xpath"""
        self.assertRaises(XPathError, self.doc.xpathReplaceTree, "//cnx:para[2]", cnxml)

    def testReplaceTreeNoText(self):
        """xpathReplaceTree() must raise ValueError if non-XML provided"""
        self.assertRaises(ValueError, self.doc.xpathReplaceTree, "/cnx:document/cnx:content/cnx:para", "")

    def testReplaceNoNS(self):
        """xpathReplaceTree() should put a tree with namespace into the default namespace"""
        self.doc.xpathReplaceTree("/cnx:document/cnx:content/cnx:para", noNS)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <tag>Hello</tag>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testReplaceCNXML(self):
        """xpathReplaceTree() should correctly replace a CNXML tree"""
        self.doc.xpathReplaceTree("/cnx:document/cnx:content/cnx:para", cnxml)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="hello">Hello</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testReplaceCNXMLMathML(self):
        """xpathReplaceTree() should correctly replace a cnxml tree with an additional namespace declaration"""
        self.doc.xpathReplaceTree("/cnx:document/cnx:content/cnx:para", cnxml_mathml)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="hello">Hello</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testReplaceCNXMLMathML2(self):
        """xpathReplaceTree() should correctly replace a subtree with both CNXML and MathML"""
        self.doc.xpathReplaceTree("/cnx:document/cnx:content/cnx:para", cnxml_mathml2)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="hello">Hello<m:math><m:cn>0</m:cn></m:math></para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testReplaceNestedCNXML(self):
        """xpathReplaceTree() should correctly replace a subtree with nested CNXML"""
        self.doc.xpathReplaceTree("/cnx:document/cnx:content/cnx:para", nested_cnxml)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <section id="s1"><para id="hello">Hello</para></section>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testReplaceCNXMLDTD(self):
        """xpathReplaceTree() should correctly replace a subtree with CNXML that includes a DTD"""
        self.doc.xpathReplaceTree("/cnx:document/cnx:content/cnx:para", cnxml_dtd)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="hello">Hello</para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)

    def testReplaceCNXMLMathMLDTD(self):
        """xpathReplaceTree() should correctly replace a subtree with CNXML that includes the MathML DTD"""
        self.doc.xpathReplaceTree("/cnx:document/cnx:content/cnx:para", cnxml_mathml_dtd)

        correct = """<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/">
  <content>
    <para id="hello">Hello<m:math><m:cn>0</m:cn></m:math></para>
  </content>
</document>
"""
        result = self.doc.getSource()
        self.assertEquals(result, correct)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(XPathNodeEditorInterface))
    suite.addTest(makeSuite(XPathInsertTree))
    suite.addTest(makeSuite(XPathAppendTree))
    suite.addTest(makeSuite(XPathDeleteTree))
    suite.addTest(makeSuite(XPathReplaceTree))
    return suite

if __name__ == '__main__':
    framework()
