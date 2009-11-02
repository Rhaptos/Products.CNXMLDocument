#------------------------------------------------------------------------------#
#   test_cnxml_document.py                                                     #
#                                                                              #
#       Authors:                                                               #
#       Rajiv Bakulesh Shah <raj@enfoldsystems.com>                            #
#                                                                              #
#           Copyright (c) 2009, Enfold Systems, Inc.                           #
#           All rights reserved.                                               #
#                                                                              #
#               This software is licensed under the Terms and Conditions       #
#               contained within the "LICENSE.txt" file that accompanied       #
#               this software.  Any inquiries concerning the scope or          #
#               enforceability of the license should be addressed to:          #
#                                                                              #
#                   Enfold Systems, Inc.                                       #
#                   4617 Montrose Blvd., Suite C215                            #
#                   Houston, Texas 77006 USA                                   #
#                   p. +1 713.942.2377 | f. +1 832.201.8856                    #
#                   www.enfoldsystems.com                                      #
#                   info@enfoldsystems.com                                     #
#------------------------------------------------------------------------------#
"""Unit tests.
$Id: $
"""


from Products.RhaptosTest import config
import Products.CNXMLDocument
config.products_to_load_zcml = [('configure.zcml', Products.CNXMLDocument),]
config.products_to_install = ['CNXMLDocument']
config.extension_profiles = ['Products.CNXMLDocument:default']

from Products.CNXMLDocument.CNXMLFile import CNXMLFile
from Products.CNXMLDocument.interfaces.ICNXMLFile import ICNXMLFile
from Products.CNXMLDocument.interfaces.IParameterManager import IParameterManager
from Products.RhaptosTest import base


class TestCNXMLDocument(base.RhaptosTestCase):

    def afterSetUp(self):
        pass

    def beforeTearDown(self):
        pass

    def test_portal_cnxml_file_interfaces(self):
        # Make sure that CNXML file implements the expected interfaces.
        self.failUnless(ICNXMLFile.isImplementedByInstancesOf(CNXMLFile))
        self.failUnless(IParameterManager.isImplementedByInstancesOf(CNXMLFile))

    def test_portal_cnxml_file(self):
        self.assertEqual(1, 1)

    def test_xml_service(self):
        self.assertEqual(1, 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCNXMLDocument))
    return suite
