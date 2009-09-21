## Script (Python) "validate_registration"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=validates the CNXML text
REQUEST=context.REQUEST

validator = context.portal_form.createForm()
errors = validator.validate(REQUEST, REQUEST.get('errors', None))

if errors:
    psm = context.translate("message_please_correct_errors", domain="rhaptos", default="Please correct the indicated errors.")
    return ('failure', errors, {'portal_status_message':psm})
else:
    if REQUEST.saveaction=='Upload File':
        msg = context.translate("message_file_uploaded", domain="rhaptos", default="File uploaded.")
    else:
        msg = context.translate("message_file_saved", domain="rhaptos", default="File saved.")
    return ('success', errors, {'portal_status_message':msg})
