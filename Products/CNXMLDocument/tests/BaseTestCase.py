# BaseTestCase
from Testing import ZopeTestCase
from Products.CNXMLDocument.CNXMLFile import CNXMLFile
import libxml2

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
        libxml2.debugMemory(1)

    def beforeTearDown(self):
        libxml2.cleanupParser()
        if libxml2.debugMemory(1):
            print "Memory leak %d bytes" % (libxml2.debugMemory(1))
        libxml2.dumpMemory()
