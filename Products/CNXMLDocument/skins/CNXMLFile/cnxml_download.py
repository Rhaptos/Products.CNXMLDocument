# Download the file
context.REQUEST.RESPONSE.setHeader("Content-Disposition", "attachment; filename=%s" % context.getId())
context.REQUEST.RESPONSE.setHeader("Content-Type", "mozilla-ignores-content-disposition")
return context.getSource()
