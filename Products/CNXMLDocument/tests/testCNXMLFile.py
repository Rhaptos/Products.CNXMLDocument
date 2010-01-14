# Load fixture

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from BaseTestCase import BaseTestCase
from Products.CNXMLDocument.CNXMLFile import CNXMLFile

class CNXMLFileTestCase(BaseTestCase):
    """
    Unit tests for CNXMLFile Zope Product.  These tests use the
    ZopeTestCase enhanced testing product.
    """

    def afterSetUp(self):
        pass

    def afterClear(self):
        pass

    def testImplementsIXMLFile(self):
        from Products.CNXMLDocument.interfaces.ICNXMLFile import ICNXMLFile
        self.failUnless(ICNXMLFile.isImplementedByInstancesOf(CNXMLFile))

    def testImplementsIParameterManager(self):
        from Products.CNXMLDocument.interfaces.IParameterManager import IParameterManager
        self.failUnless(IParameterManager.isImplementedByInstancesOf(CNXMLFile))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(CNXMLFileTestCase))
    return suite

if __name__ == '__main__':
    framework()
