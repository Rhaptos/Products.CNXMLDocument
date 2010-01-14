"""
Zope 3 Component Architecture interfaces for CNXMLDocument, including general MDML.

Author: J. Cameron Cooper (jccooper@rice.edu)
Copyright (C) 2009 Rice University. All rights reserved.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""
# "newinterfaces" because of our existing "interfaces" module, which uses older interface mechanisms

from zope.interface import Interface

class IMDML(Interface):
    """Marker interface for objects that can generate an MDML block."""
    pass

class ICNXMLContainer(Interface):
    """Marker interface for CNXMLDocument-like objects."""
    pass

class ICNXMLAbstract(Interface):
    """Marker interface for content objects which have CNXML-containing abstracts."""
    pass
