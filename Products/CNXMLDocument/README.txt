CNXMLDocument

  This Zope Product is part of the Rhaptos system
  (http://software.cnx.rice.edu)

  CNXMLDocument provides a content type for files written in CNXML:
  http://cnx.rice.edu/cnxml

  CNXMLFile objects provide an interface for performing DTD
  validation, XSLT stylesheet transformation, and various operations
  on nodes via XPath.

Requirements:

  - libxml and libxslt and their python bindings: ftp://xmlsoft.org/

  - lxml Python package: http://codespeak.net/lxml/

  - CNXML and MathML schemas and stylesheets: http://software.cnx.rice.edu/
    Use of local resources through XML Catalog highly recommended.

Future plans

  - Refactor XMLService into a tool

  - Move common portions of CNXMLFile into more generic XMLFile

  - Improve support for using CNXMLFile outside Rhaptos modules