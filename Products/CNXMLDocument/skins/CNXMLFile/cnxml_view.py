## Script (Python) "cnxml_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=transforms and displays the CNXML file
from Products.CNXMLDocument.XMLService import XMLError

try:
    return context.cnxml_transform(context.getSource(), **kw)
except XMLError:
    url = context.absolute_url()
    psm = context.translate("message_errors_prevent_view", domain="rhaptos", default="Errors in the file prevent it from being viewed")
    return context.REQUEST.RESPONSE.redirect(url+'/cnxml_edit_form?portal_status_message='+psm)
