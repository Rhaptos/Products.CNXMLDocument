#Change file content""
# FIXME: notify parent that we've changed so it can change revised, log an action, and update the DOCTYPE
content = context.getNewContents()
context.manage_edit('', 'text/xml', filedata=content)

