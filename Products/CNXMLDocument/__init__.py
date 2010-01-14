"""
Initialize a CNXML Document Product

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import CNXMLFile
import PortalCNXMLFile
import libxml2
import os

from Globals import package_home
from Products.CMFCore import utils, CMFCorePermissions
from Products.CMFCore.DirectoryView import registerDirectory
import sys

from AccessControl import ModuleSecurityInfo

this_module = sys.modules[ __name__ ]

# Setup XSL transform path
CNXML_UPGRADE_XSL =  os.path.join(package_home(globals()), 'www/cnxmlupgrade.xsl')
ModuleSecurityInfo('Products.CNXMLDocument').declarePublic('CNXML_UPGRADE_XSL')
CNXML_SEARCHABLE_XSL =  os.path.join(package_home(globals()), 'www/baretext.xsl')
ModuleSecurityInfo('Products.CNXMLDocument').declarePublic('CNXML_SEARCHABLE_XSL')
CNXML_RENDER_XSL =  'http://cnx.rice.edu/technology/cnxml/stylesheet/cnxml_render.xsl'
ModuleSecurityInfo('Products.CNXMLDocument').declarePublic('CNXML_RENDER_XSL')

contentConstructors = (PortalCNXMLFile.addCNXMLFile,)
contentClasses = (PortalCNXMLFile.PortalCNXMLFile,)

product_globals = globals()

z_bases = utils.initializeBasesPhase1(contentClasses, this_module)

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())
registerDirectory('skins/CNXMLFile', globals())

# Allow access to XMLService (until it's a tool)
from AccessControl import allow_module, allow_class
from Products.CNXMLDocument import XMLService
allow_module('Products.CNXMLDocument.XMLService')
allow_class(libxml2.xmlDoc)

def initialize(context):
    """
    Register base classes
    """

    utils.initializeBasesPhase2( z_bases, context )
    utils.ContentInit(PortalCNXMLFile.PortalCNXMLFile.meta_type,
                      content_types = contentClasses,
                      permission = CMFCorePermissions.AddPortalContent,
                      extra_constructors = contentConstructors,
                      fti = PortalCNXMLFile.factory_type_information).initialize(context)

    context.registerBaseClass(CNXMLFile.CNXMLFile)
    context.registerClass(CNXMLFile.CNXMLFile,
                          constructors=(CNXMLFile.manage_addCNXMLFileForm,
                                        CNXMLFile.manage_addCNXMLFile),
                          icon="www/cnxmlfile.gif")

