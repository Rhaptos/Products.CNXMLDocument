## Script (Python) "cnxml_export"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=format
##title=Export CNXML File

from Products.CNXMLTransforms.helpers import doTransform

f = context.getDefaultFile()
source = f.getSource()
objectId = context.objectId or context.getId().replace('.','-')
name = "%s-%s.cnxml" % (objectId, format) 
context.REQUEST.RESPONSE.setHeader("Content-Disposition", "attachment; filename=%s" % name)
context.REQUEST.RESPONSE.setHeader("Content-Type", "mozilla-ignores-content-disposition")

if format == 'plain':
    result = source
elif format == 'authentic':
    result = doTransform(context, "cnxml_to_authentic", source)[0]
return result
