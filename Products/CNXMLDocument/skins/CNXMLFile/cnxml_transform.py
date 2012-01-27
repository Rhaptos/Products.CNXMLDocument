## Script (Python) "cnxml_transform"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=source, stylesheet=None, **params
##title=displays the CNXML file as part of a module
from Products.CNXMLDocument.XMLService import XMLError
from Products.CNXMLDocument import XMLService
from Products.CNXMLDocument import CNXML_RENDER_XSL

MATHML_NS = 'http://www.w3.org/1998/Math/MathML'

#CNXML_XSL = 'http://cnx.rice.edu/technology/cnxml/stylesheet/unibrowser.xsl'
CNXML_XSL = CNXML_RENDER_XSL

if not stylesheet:
    stylesheet = CNXML_XSL
stylesheets = [stylesheet]

### for old CNXML (< 0.5) ###
doctype = getattr(context, 'doctype', None)
if doctype and doctype.find('0.5') == -1:
    from Products.CNXMLDocument import CNXML_UPGRADE_XSL
    stylesheets.insert(0, CNXML_UPGRADE_XSL)
### /upgrade ###

# Parse the source and grab the namespaces
doc = XMLService.parseString(source)
sourceNs = XMLService.listDocNamespaces(doc)

# Figure out our content types
has_math = MATHML_NS in sourceNs
params['doctype'], params['mimetype'], ns = context.content_type_decide(has_math=has_math)

# Transform source

result = XMLService.xsltPipeline(doc, stylesheets, **params)

# Set content-type
context.REQUEST.RESPONSE.setHeader('Content-Type', "%s; charset=utf-8" % params['mimetype'])

# Prepend doctype
header = context.xmlheader(params['doctype'])

return header+'\n'+result
