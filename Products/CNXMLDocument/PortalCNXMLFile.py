"""
Portal for CNXML Files

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import AccessControl
from Globals import InitializeClass
from OFS.Image import cookId
from Products.CMFDefault.File import File, addFile
from Products.CMFCore import permissions
from CNXMLFile import CNXMLFile, autoUpgrade, autoIds
from XMLService import XMLError

factory_type_information = (
    { 'id'             : 'CNXML Document',
      'meta_type'      : 'CMF CNXML File',
      'description'    : """File objects can contain arbitrary downloadable files.""",
      'icon'           : 'file_icon.gif',
      'product'        : 'CNXMLDocument',
      'factory'        : 'addCNXMLFile',
      'immediate_view' : 'file_edit_form',
      'actions'        : ({'id'            : 'view',
                           'name'          : 'View',
                           'action'        : 'string:${object_url}/file_view',
                           'permissions'   : (permissions.ModifyPortalContent, ),
                           },
                          {'id'            : 'download',
                           'name'          : 'Download',
                           'action'        : 'string:${object_url}',
                           'permissions'   : (permissions.ModifyPortalContent, ),
                           'visible'       : 1,
                           },
                          {'id'            : 'edit',
                           'name'          : 'Edit',
                           'action'        : 'string:${object_url}/file_edit_form',
                           'permissions'   : (permissions.ModifyPortalContent, ),
                           'visible'       : 1,
                           },
                          {'id'            : 'importexport',
                           'name'          : 'Import/Export',
                           'action'        : 'cnxml_importexport',
                           'permissions'   : (permissions.ModifyPortalContent, ),
                           'visible'       : 0,
                           },
                          {'id'            : 'preview',
                           'name'          : 'Preview',
                           'action'        : '../module_view',
                           'permissions'   : (permissions.ModifyPortalContent, ),
                           'visible'       : 0,
                           },
                          { 'id'            : 'external_edit',
                            'name'          : 'External Edit',
                            'action'        : 'external_edit',
                            'permissions'   : (permissions.ModifyPortalContent, ),
                            'visible'       : 0,
                            },
                          )
      },
    )

def addCNXMLFile(self, id, title='', file='', idprefix=None, **kw):
    """ Add a CNXML File object to the portal """

    id, title = cookId(id, title, file)
    self = self.this()

    self._setObject(id, PortalCNXMLFile(id, title, '', **kw))

    # 'Upload' the file.  This is done now rather than in the
    # constructor because the object is now in the ZODB and
    # can span ZODB objects.
    obj = self._getOb(id)
    obj.manage_upload(file, idprefix=idprefix)

    # Force content type to text/xml since form uploading gets it wrong
    obj.content_type="text/xml"


class PortalCNXMLFile(CNXMLFile, File):
    """
        A Portal-managed CNXML File
    """

    __implements__ = ( File.__implements__)
    
    meta_type='CMF CNXML File'
    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(permissions.ModifyPortalContent, 'xpathReplaceTree')
    security.declareProtected(permissions.ModifyPortalContent, 'xpathDeleteTree')
    security.declareProtected(permissions.ModifyPortalContent, 'xpathInsertTree')
    security.declareProtected(permissions.ModifyPortalContent, 'xpathAppendTree')
    #security.declareProtected(permissions.ModifyPortalContent, 'setContent')
    #security.declareProtected(permissions.ModifyPortalContent, 'setMetadata')
    #security.declareProtected(permissions.ModifyPortalContent, 'setTitle')

    def __init__(self, *args, **kw):
        CNXMLFile.__init__(self, *args, **kw)
        File.__init__(self, *args, **kw)
        # Manually set the ID because File is currently broken and deleting __name__,
        # which is where the id is actually stored.  We should probably migrate this to
        # using the ATCT File, which does work.
        self.__name__ = args[0]

    def setSource(self, source, idprefix=None):
        """Set the document's source; override of CNXMLFile version, to add prefix passing.
        The best method to use to set the body of the CNXMLFile.
        """
        self.manage_upload(source, idprefix=idprefix)

    def manage_upload(self, file='', REQUEST=None, idprefix=None):
        """
        Replaces the current contents of the File or Image object with file.

        The file or images contents are replaced with the contents of 'file'.

        Override of OFS.Image version (through parent) to add automatic
        ids, with prefixes.

        A reasonable method to use to set the body of the CNXMLFile, but 'setSource' recommended
        if you don't need to be strictly File-ish.
        """
        # manage_upload can take file-ish as well as str
        read = getattr(file, 'read', None)
        if read:
            cursor = file.tell()   # so we can put the seek back where we found it
            file.seek(0)
            src = file.read()
            file.seek(cursor)
        else:
            src = file

        src = autoIds(src, prefix=idprefix)
        if type(src) is unicode:   # OFS.Image.File._read_data isn't happy with possible unicode
            src = src.encode('utf-8')
        return CNXMLFile.manage_upload(self, file=src, REQUEST=REQUEST)

    def manage_edit(self, title, content_type, precondition='',
                    filedata=None, REQUEST=None, idprefix=None):
        """
        Changes the title and content type attributes of the File or Image.

        Override of OFS.Image version (through parent) to add automatic
        ids, with prefixes.

        A reasonable method to use to set the body of the CNXMLFile, but 'setSource' recommended
        if you don't need to be strictly File-ish.
        """
        filedata = autoIds(filedata, prefix=idprefix)
        return CNXMLFile.manage_edit(self, title, content_type, precondition=precondition,
                                     filedata=filedata, REQUEST=REQUEST)

    def manage_afterAdd(self, item, container):
        """Both of my parents have an afterAdd method"""
        CNXMLFile.manage_afterAdd(self, item, container)
        File.manage_afterAdd(self, item, container)

    def manage_beforeDelete(self, item, container):
        """Both of my parents have a beforeDelete method"""
        File.manage_beforeDelete(self, item, container)
        CNXMLFile.manage_beforeDelete(self, item, container)


InitializeClass(PortalCNXMLFile)

