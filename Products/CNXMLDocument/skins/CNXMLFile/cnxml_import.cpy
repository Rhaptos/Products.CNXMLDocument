## Script (Python) "module_import"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=format, importFile
##title=Import module contents

from Products.CNXMLTransforms.helpers import doTransform

text = importFile.read()
if not text:
    psm = context.translate("message_error_select_file_to_import", domain="rhaptos", default="Error: you must select a file to import")
    return state.set(status='failure', portal_status_message=psm)

if format == 'plain':
    context.manage_edit('', 'text/xml', filedata=text)
elif format == 'authentic':
    try:
        text = doTransform(context, "authentic_to_cnxml", text)[0]
    except ValueError:
        psm = context.translate("message_error_select_correct_format", domain="rhaptos", default="Error parsing file. Be sure to select the correct import format.")
        return state.set(status='failure', portal_status_message=psm)
    context.manage_edit('', 'text/xml', filedata=text)

psm = context.translate("message_file_imported", domain="rhaptos", default="File Imported.")
return state.set(portal_status_message=psm)
