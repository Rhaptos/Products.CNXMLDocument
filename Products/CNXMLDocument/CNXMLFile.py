"""
A CNXML File Object

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Image import File, cookId
from Globals import package_home
from AccessControl import ModuleSecurityInfo
from zope.interface import implements
from interfaces.ICNXMLFile import ICNXMLFile
from interfaces.IParameterManager import IParameterManager
from interfaces.IXPathNodeEditor import IXPathNodeEditor
from Products.CNXMLDocument.newinterfaces import IMDML
import os
import re
import types
import logging
import XMLService
from lxml import etree
from CNXMLVersionRecognizer import Recognizer

log = logging.getLogger('CNXMLDocument.CNXMLFile')

manage_addCNXMLFileForm = PageTemplateFile('zpt/manage_addCNXMLFileForm',
                                           globals(),
                                           __name__='manage_addCNXMLFileForm')

## CNXML part recognition regexes
doctypeRegexp = re.compile(r"PUBLIC\s*['\"]([^>'\"]*)['\"]")
cnxDTDRegexp = re.compile(r"//DTD CNXML (\S*?)[ /]")

nameRegexp = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.UNICODE)

# The metadata matching is non-greedy because we only want the first
# occurance at the beginning of the module
metadataRegexp = re.compile(r"(<metadata.*?</metadata>)", re.DOTALL | re.UNICODE)
missingmetadataRegexp = re.compile(r"(?<=</title>)\s*", re.DOTALL | re.UNICODE)
featuredlinksRegexp = re.compile(r"(<featured\-links.*?</featured\-links>)", re.DOTALL | re.UNICODE)
missingfeaturedlinksRegexp = re.compile(r"\s*(?=<content)", re.DOTALL | re.UNICODE)

# The content matching is greedy because we must match the entire
# content section, event if it includes an </content> tag
contentRegexp = re.compile(r"(<content>.*</content>)", re.DOTALL | re.UNICODE)

## other constants
STYLESHEET_BASE = "/usr/local/share/swi"

## upgrade service
UPGRADE_05_TO_06_XSL = 'http://cnx.rice.edu/technology/cnxml/stylesheet/cnxml05to06.xsl'
UPGRADE_06_TO_07_XSL = 'http://cnx.rice.edu/technology/cnxml/stylesheet/cnxml06to07.xsl'

## FIXME EVIL EVIL NAMESPACE HARDCODED PREFIXES FOR EIP

NAMESPACES = {'cnx':'http://cnx.rice.edu/cnxml',
              'md':'http://cnx.rice.edu/mdml/0.4',
              'bib':'http://bibtexml.sf.net/',
              'm':'http://www.w3.org/1998/Math/MathML',
              'x':'http://www.w3.org/1999/xhtml',
              'q':'http://cnx.rice.edu/qml/1.0'}

def autoUpgrade(source, **params):
    """Turn older CNXML (0.5/0.6) into newer (0.7).
    Checks version to determine if upgrade is needed.
    With a newer version, we may add additional stylesheets to the pipeline.
    Return tuple of (new_source, boolean_was_converted)
    """
    version = Recognizer(source).getVersion() # if wrong, we could end up doing this on every save
    stylesheets = []
    if version == '0.7':
        pass # Do nothing. 0.7 is the latest
    elif version == '0.6':
        stylesheets.append(UPGRADE_06_TO_07_XSL)
    else:
        stylesheets.append(UPGRADE_05_TO_06_XSL)
        stylesheets.append(UPGRADE_06_TO_07_XSL)

    if source and stylesheets:
        try:
            doc = XMLService.parseString(source)
            result = XMLService.xsltPipeline(doc, stylesheets, **params)
            return result, True
        except XMLService.XMLParserError:
            pass  # just stopping on parse error is okay; it'll send us to the fallback below
    return source, False

## auto-id service
CNXML_AUTOID_XSL = os.path.join(package_home(globals()), 'www/generateIds.xsl')
ModuleSecurityInfo('Products.CNXMLDocument.CNXMLFile').declarePublic('autoIds')
def autoIds(source, prefix=None, force=False, **params):
    """For CNXML, fill in ids where the author has left none. Only for CNXML 0.6, and will check
    for CNXML version unless instructed otherwise.
    'prefix' will add the passed-in string to the beginning of the ids
    'force' doesn't check version itself, relies on caller to certify the XML is okay.
    """
    transformable = force or Recognizer(source).getVersion() in ('0.6', '0.7')
    # we want to make sure recognizer keeps working right; if wrong, we end up doing this on every save

    if prefix:
        params['id-prefix'] = prefix
    stylesheets = [CNXML_AUTOID_XSL]
    if source and stylesheets and transformable:
        try:
            doc = XMLService.parseString(source)   # may error if malformed
            # TODO: if slow, we could replace with Expat 2-pass method
            result = XMLService.xsltPipeline(doc, stylesheets, **params)
            return result
        except XMLService.XMLParserError:
            pass  # just stopping on parse error is okay; it'll send us to the fallback below
    return source

## error logging/handling

etree.use_global_python_log(etree.PyErrorLog())

class CNXMLFileError(Exception):
    pass

class XPathError(Exception):
    pass

## and, finally, the class...
def manage_addCNXMLFile(self,id,file='',title='',precondition='', content_type='text/xml', REQUEST=None):
    """Add a new CNXML File object.
    Creates a new CNXML File object 'id' with the contents of 'file'
    """

    id=str(id)
    title=str(title)
    content_type=str(content_type)
    precondition=str(precondition)

    (id, title) = cookId(id, title, file)

    self=self.this()

    # First, we create the file without data:
    self._setObject(id, CNXMLFile(id,title,'',content_type, precondition))

    # Now we "upload" the data.  By doing this in two steps, we
    # can use a database trick to make the upload more efficient.
    self._getOb(id).manage_upload(file)
    if content_type:
        self._getOb(id).content_type=content_type

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


class CNXMLFile(File):
    """CNXML File"""

    implements(IMDML)
    __implements__ = ICNXMLFile, IParameterManager, IXPathNodeEditor

    meta_type = "CNXML File"

    manage_parametersForm = PageTemplateFile('zpt/manage_parametersForm', globals())
    manage_look = PageTemplateFile('zpt/manage_look', globals())

    # Template for cnxml
    cnxmlTemplate = PageTemplateFile('zpt/cnxmlTemplate', globals())
    cnxmlTemplate.content_type = "text/xml"
    cnxmlTemplate.title = "Cnxml Template"

    # Template for featured links
    featuredlinksTemplate = PageTemplateFile('zpt/featuredlinksTemplate', globals())
    featuredlinksTemplate.content_type = "text/xml"
    featuredlinksTemplate.title = "Featured Links Template"

    options = list(File.manage_options);
    manage_options = tuple(options[:3]
                           + [{'label':'Parameters','action':'manage_parametersForm'}]
                           + options[3:])

    def __init__(self, *args, **kwargs):
        self._parameters = {}
        return File.__init__(self, *args, **kwargs)

    def validate(self):
        """Validate the CNXML document"""
        return XMLService.validate(self.getSource())

    def createTemplate(self, **kw):
        """Set the file data via a template"""
        data = self.cnxmlTemplate(**kw).encode('utf-8')
        self.manage_upload(data)

    def normalize(self):
        """Return 'normalized' document with entities expanded, etc."""
        return XMLService.normalize(self.getSource())

    def source(self):
        """Return document's source"""
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        return self.normalize()

    def getSource(self):
        """Return document content"""
        data = self.data
        if type(data) is unicode:
            data = data.encode('utf-8')
        else:
            data = str(data)  # possibly a Pdata
        return data

    def setSource(self, source, idprefix=None):
        """Set the document's source.
          'idprefix' is ignored in this object. See PortalCNXMLFile.
        """
        if type(source) is unicode:   # OFS.Image.File._read_data isn't happy with possible unicode
            source = source.encode('utf-8')
        self.manage_upload(source)

    def getVersion(self):
        """Return CNXML version of the stored document, either based on doctype or attribute, as found.
        Not a property, but XML introspection.
        """
        return Recognizer(self.getSource()).getVersion()  # TODO: remember this... without staleness (hash?)

    def upgrade(self, backupto=None, backupname='index.cnxml.old'):
        """Upgrade the contained CNXML to the current version, if possible.
        Version is auto-detected by 'CNXMLVersionRecognizer'.
        Uses the 'autoUpgrade' function in this module.
          'backupto' is a containerish object where we will create a File containing the current contents.
             We presume to have the permissions to do this.
          'backupname' is the id of that file; default is 'index.cnxml.old'
        Returns true value if upgrade was run, false value if not run (because it is current, or failed.)
        """
        origsource = self.getSource()
        if backupto and backupname:
            backup = getattr(self, backupname, None)
            if not backup:
                backupto.invokeFactory(id=backupname, type_name='UnifiedFile')
                backup = backupto[backupname]
                backup.update_data(origsource)
                backup.reindexObject()

        source, converted = autoUpgrade(origsource)
        if converted:
            source = self.setMetadata(returnonly=True, source=source)
            self.setSource(source)
        return converted

    def _xpathEval(self, doc, xpath):
        """Evaluate a XPath expression and return the results"""
        result = doc.xpath(xpath,namespaces=NAMESPACES)
        return result

    def _getXPathNode(self, doc, xpath):
        """Get a node from an XPath expression"""
        result = self._xpathEval(doc, xpath)
        if not result:
            raise XPathError, "Cannot find node: %s" % xpath

        return result[0]

    def _getXPathNodes(self, doc, xpath):
        """Get nodes from an XPath expression"""
        results = self._xpathEval(doc, xpath)
        if not results:
            # this is a clear case where using exceptions to handle a non-exceptional case
            # is the wrong-thing-to-do
            log.info("_getXPathNodes found nothing. throwing an exception.")
            raise XPathError, "Cannot find node: %s" % xpath
        return results

    def _parseDoc(self):
        """
        Return the parsed XML document

        """
        return XMLService.parseString(self.getSource())

    def rootNode(self):
        doc = self._parseDoc()
        content = etree.tostring(doc.getroot())

        return content

    def xpathGetTree(self, xpath, namespaces=False):
        """Get the text of a tree in the source matching the given xpath.
        Provide 'namespaces' as true to get a serialization
        """
        doc = self._parseDoc()
        try:
            node = self._getXPathNode(doc, xpath)
        except (CNXMLFileError, XPathError):
            raise
        content = etree.tostring(node)

        # this prevents IE from caching the result
        request = getattr(self, 'REQUEST', None)
        if request:
            request.RESPONSE.setHeader('Cache-Control', 'no-cache')
            request.RESPONSE.setHeader('Pragma', 'no-cache')

        return content

    def xpathReplaceTree(self, xpath, xmlText, idprefix=None):
        """Replace the text of a tree in the source matching the given id.
        Return XPath to the replaced node in the document.
        """
        log.debug("CNXML: Replacing node at '%s'" % xpath)
        doc = self._parseDoc()
        try:
            node = self._getXPathNode(doc, xpath)
        except (CNXMLFileError, XPathError):
            raise

        try:
            newNode = etree.fromstring(xmlText)
        except etree.XMLSyntaxError, e:
            raise ValueError, "Bad xml:%s" % xmlText

        node.getparent().replace(node,newNode)
        newxpath = doc.getpath(newNode)

        source = etree.tostring(doc)
        self.setSource(source, idprefix=idprefix)
        
        return newxpath

    def xpathDeleteTree(self, xpath):
        """Delete the node specified by the xpath"""
        log.debug("CNXML: Deleting node at '%s'" % xpath)
        source = self.getSource()
        doc = self._parseDoc()
        try:
            node = self._getXPathNode(doc, xpath)
        except (CNXMLFileError, XPathError):
            raise

        node.getparent().remove(node)
        source = etree.tostring(doc)
        self.setSource(source)

    def xpathInsertTree(self, xpath, xmlText, idprefix=None):
        """Insert a tree into the document.
        Return XPath to the replaced node in the document.
        """
        return self._addTree(xpath, 'before', xmlText, idprefix=idprefix)

    def xpathAppendTree(self, xpath, xmlText, idprefix=None):
        """Append a tree into the document.
        Return XPath to the replaced node in the document.
        """
        return self._addTree(xpath, 'after', xmlText, idprefix=idprefix)

    def _addTree(self, xpath, position, xmlText, idprefix=None):
        """Add the specified tree at the position before or after the xpath
        Return XPath to the replaced node in the document.
        """
        log.debug("CNXML: Adding tree at '%s'" % xpath)
        doc = self._parseDoc()
        try:
            node = self._getXPathNode(doc, xpath)
        except (CNXMLFileError, XPathError):
            raise

        try:
            newNode = etree.fromstring(xmlText)
        except etree.XMLSyntaxError, e:
            raise ValueError, "Bad xml:%s" % xmlText

        if position =='before':
            node.addprevious(newNode)
        else:
            node.addnext(newNode)
        
        newxpath = doc.getpath(newNode)

        source = etree.tostring(doc)
        self.setSource(source, idprefix=idprefix)

        return newxpath

    def getParameters(self):
        """Return parameters"""
        return self._parameters.copy()


    def manage_addParameter(self,key='',value='',type='',REQUEST=None):
        """Add a new parameter via the web"""
        if key=='' or self._parameters.has_key(key):
            raise 'Bad Request', 'Invalid or duplicate parameter name'
        self._addParameter(key,value,type)
        if REQUEST is not None:
            return self.manage_parametersForm(self, REQUEST)


    def _addParameter(self,key,value,type='string'):
        """Add a parameter to this object"""
        if type=='int':
            try:
                self._parameters[key] = int(value)
            except:
                raise TypeError, 'Value is not an integer.'
        else:
            self._parameters[key] = value


    def manage_delParameters(self,keys=None,REQUEST=None):
        """Delete the specified parameter(s) via the web"""
        if keys is None:
            raise 'Bad Request', 'No parameters were specified.'
        self._delParameters(keys)
        if REQUEST is not None:
            return self.manage_parametersForm(self, REQUEST)


    def _delParameters(self,keys):
        """Delete the specified parameter(s) from this object"""
        for key in keys:
            del self._parameters[key]


    def manage_editParameters(self,values=None,REQUEST=None):
        """Edit the specified parameter(s) via the web"""
        if values is None:
            raise 'Bad Request', 'No parameters were specified.'
        self._editParameters(values)
        if REQUEST is not None:
            return self.manage_parametersForm(self, REQUEST)


    def _editParameters(self,values):
        """Edit the specified parameter(s) associated with this object"""
        keys = self._parameters.keys()
        for key, value in map(None, keys, values):
            if isinstance(self._parameters[key],types.IntType):
                # if the old value is an integer, try it as an integer
                try:
                    self._parameters[key] = int(value)
                except:
                    raise TypeError, 'Integer value is expected in this field.'
            else:
                # string type
                self._parameters[key] = value


    def getContent(self):
        """Get the <content> portion of the CNXML document"""
        source = self.getSource()
        try:
            return contentRegexp.search(source).groups()[0]
        except IndexError:
            return None


    def setContent(self, content):
        """Set the <content> portion of the CNXML document"""
        source = self.getSource()
        text = contentRegexp.sub(content, source)
        self.update_data(text)


    def setMetadata(self, metadata=None, returnonly=False, source=""):
        """Set the <metadata> portion of the CNXML document.
         'metadata' is IGNORED! Deprecated!
         'returnonly' is boolean where true returns the updated text only;
             false sets the text on self, and is the default and normal way.
         'source' is optional text of the CNXML to set metadata on; usually used
             with 'returnonly'. Default is source of 'self' object.
        The 'returnonly' and 'source are sort of turn-into-function args, pretty
        much only for use in a situation where we're already doing an 'update_data'.
        """
        if metadata:
            log.warning("DEPRECATION WARNING: CNXMLDocument.CNXMLFile.setMetadata: 'metadata' arg is deprecated.")
        source = source or self.getSource()
        version = Recognizer(source).getVersion()
        text = source
        if version is None or float(version) >= float('0.7'):
            mdxml = self.restrictedTraverse('metadata')().rstrip()
            mdxml = '\n'.join([l for l in mdxml.split('\n') if l.strip()])  # elim. blank lines
            
            # make sure we have the same type for regex sub...
            if type(mdxml) is not unicode:
                mdxml = mdxml.decode('utf-8')
            if type(source) is not unicode:
                source = source.decode('utf-8')

            match = metadataRegexp.search(source)
            if match is None:
                log.warning("CNXMLFile: Metadata is missing and will be added back.")
                text = missingmetadataRegexp.sub("\n%s\n" % mdxml, source, 1)
            else:
                text = metadataRegexp.sub(mdxml, source)

            if not returnonly:
                self.update_data(text)
        elif version in ('0.4', '0.5', '0.6'):  # FIXME: handle older metadata?
            log.warning("CNXMLFile: Metadata setting not supported for old CNXML version %s" % version)
        else:  # FIXME: older versions?
            log.warning("CNXMLFile: Metadata setting not supported for %s" % version or 'unknown version')

        if returnonly:
            return text

    def getMetadata(self):
        """Get the <metadata> portion of the CNXML document"""
        source = self.getSource()
        try:
            return metadataRegexp.search(source).groups()[0]
        except IndexError:
            return None


    def setTitle(self, title):
        """Set the <name> portion of the CNXML document"""
        source = self.getSource()

        # Convert title to unicode if necessary
        if not isinstance(title, unicode):
          title = unicode(title, 'utf-8')
        title = title.encode('utf-8')

        title = title.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        # Convert source to unicode if necessary
        if not isinstance(source, unicode):
          source = unicode(source, 'utf-8')
        source = source.encode('utf-8')

        text = nameRegexp.sub("<title>%s</title>" % title, source, 1)
        self.update_data(text)


    def getTitle(self):
        """Get the <name> portion of the CNXML document"""
        source = self.getSource()
        try:
            return nameRegexp.search(source).groups()[0]
        except IndexError:
            return None


    def getDoctype(self):
        """Return DOCTYPE string"""
        try:
            return doctypeRegexp.search(self.getSource()).group(1)
        except (AttributeError, IndexError):
            return None


    def setDoctype(self, system, public=None):
        """Set DOCTYPE string"""
        pass

    def setFeaturedLinks(self, links, typedict=None):
        """Set the <featured-links> portion of the CNXML document.
         'links' takes list of links with attrs/keys 'url', 'title', 'type', 'strength'.
         'typedict' takes a dict of keys=type (as in 'links' dicts), value=label.
        Inserts or replaces 'featured-links' elt between 'metadata' and 'content'.
        Content example::
             ...
           </metadata>
           <featured-links>
              <link-group type="example">
                  <link document="m10882" version="latest" strength="3"></link>
                  <link document="m10881" version="latest" strength="2">Good Module</link>
              </link-group>
              <link-group type="certifications">
                  <label> Certifications available </label>
                  <link src="http://tinyurl.com/something" strength="2"> First Certification </link>
              </link-group>
            </featured-links>
            <content>
              ...
        We don't currently expect more than a strict vocabulary of three types 'example',
        'supplemental', and 'Prerequisite', though the method will try to support that.
        """
        # skip pre-0.6 content
        source = self.getSource()
        version = Recognizer(source).getVersion()
        if version and float(version) < float('0.6'):
            return

        # build insert text
        types = set([x['type'] for x in links])
        categories = {}    # categories contains type:{'label':category label, 'list':list of links}
        for l in links:
            t = l['type']
            if not categories.has_key(t):        # if type maps, use that for label...
                categories[t] = {'label':typedict and typedict.get(t, None), 'links':[]}
            categories[t]['links'].append(l)
        linktext = self.featuredlinksTemplate(categories=categories)
        linktext = '\n'.join([l for l in linktext.split('\n') if l.strip()])  # elim. blank lines

        # insert text
        exists = featuredlinksRegexp.search(source)
        if exists:
            text = featuredlinksRegexp.sub(linktext, source, 1)
        else:
            text = missingfeaturedlinksRegexp.sub("\n%s\n" % linktext, source, 1)
        self.update_data(text)


    def getFeaturedLinks(self):
        """Get the <featured-link> portion of the CNXML document as string, if present. None otherwise."""
        source = self.getSource()
        try:
            results = featuredlinksRegexp.search(source)
            if results:
                return results.groups()[0]
            else:
                return None
        except IndexError:
            return None

    def findReferencedWorkFiles(self, context):
        setResult = set() # set object can not have duplicates
        xpath = "//cnx:media"
        doc = self._parseDoc()
        try:
            nodes = self._getXPathNodes(doc, xpath)
        except:
            log.info("findReferencedWorkFiles experienced an exception in _getXPathNodes().")
            nodes = None
        if nodes:
            for node in nodes:
                strFile = node.get('src')
                if strFile:
                    strBaseFile = strFile.split('/')[-1]
                    # massage strFile; remove http if possible (Python Gods chortle, from on high)
                    if strFile.startswith('http://cnx.org/'):
                        strFile = strFile.replace('http://cnx.org/', '', 1)
                    if strFile.startswith('http://cnx.rice.edu/'):
                        strFile = strFile.replace('http://cnx.rice.edu/', '', 1)
                    if not strFile.startswith('http://'):
                        # '/' and './' make sense between browser & server, but not to restrictedTraverse()
                        if strFile.startswith('/'):
                             strFile = strFile.replace('/', '', 1)
                        if strFile.startswith('./'):
                             strFile = strFile.replace('./', '', 1)
                        try:
                            objFile = context.restrictedTraverse(strFile)
                        except:
                            log.info("findReferencedWorkFiles restrictedTraverse() fails.")
                            objFile = None
                        if objFile:
                            strPortalType = objFile.aq_parent.portal_type # 'Workspace' or 'Module' or 'Workgroup'
                            if strPortalType == 'Workspace' or strPortalType == 'Workgroup':
                                strFile = objFile.absolute_url(1)
                                setResult.add(strFile)
                                objFile = None
                                node.set('src',strBaseFile)
        listResults = list(setResult)
        if listResults:
            strCnxml = etree.tostring(doc)
            self.setSource(strCnxml)
        return listResults
