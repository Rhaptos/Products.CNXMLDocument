#Return either the uploaded file or the textarea contents
if (context.REQUEST.saveaction=='Upload File' and context.REQUEST.has_key('uploadedFile')):
    return context.REQUEST.uploadedFile.read()
else:
    return context.REQUEST.textareaContents
