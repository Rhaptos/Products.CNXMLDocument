# BaseTestCase
from Testing import ZopeTestCase
from Products.CNXMLDocument.CNXMLFile import CNXMLFile

baseDoc = \
"""<?xml version="1.0"?>
<!DOCTYPE document PUBLIC "-//CNX//DTD CNXML 0.5 plus MathML//EN" "http://cnx.rice.edu/cnxml/0.5/DTD/cnxml_mathml.dtd">
<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML">
  <content>
    <para id="world">World</para>
  </content>
</document>
"""

class BaseTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.doc = CNXMLFile('test', '', baseDoc)
