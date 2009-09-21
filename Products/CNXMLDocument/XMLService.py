#!/usr/bin/env python
"""
XMLService - wrapper around libxml2 to provide basic XML services

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import os
import libxml2
import libxslt
#from lxml import etree
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
#from cStringIO import StringIO

import logging
xsltlog = logging.getLogger('xslt')
log = logging.getLogger('CNXMLDocument.XMLService')

class XMLError(Exception):
    """XML Operation failed"""
    pass

class XMLParserError(XMLError):
    pass

class XMLValidityError(XMLError):
    pass

class XSLTError(XMLError):
    pass

# set Jing JAR path and test to make sure it's good on startup
JING_DEFAULT = "/opt/jing/bin/jing.jar"
JINGJARPATH = os.environ.get('JING_JAR', JING_DEFAULT)

try:  # make sure to only run the test once; module might perhaps be inited again
    if JING_TESTED:  # just to get the name called
        pass         # we now know Jing already tested
except NameError:  # JING_TESTED not assigned yet==not yet tested
    JING_TESTED = 1
    process = Popen(["java", "-jar", JINGJARPATH], stdout=PIPE, stderr=PIPE)
    process.wait()
    err = process.stderr.read()
    if err:
        log.error('Error attempting to run Jing. Java message: "%s"' % err)
        raise XMLParserError("Jing JAR file not found at %s; place it there or set environment variable 'JING_JAR' to the path where it is located. See Jing at http://www.thaiopensource.com/relaxng/jing.html" % JINGJARPATH)

# Default options for libxml2 parsing
PARSER_OPTIONS = libxml2.XML_PARSE_DTDLOAD | \
                 libxml2.XML_PARSE_NOENT | \
                 libxml2.XML_PARSE_NONET & \
                 ~libxml2.XML_PARSE_DTDATTR

class XMLParser:
    """Internal implementation class for XMLService."""

    def __init__(self, options=None, catalog=None):
        """
        Initialize an XML parser

        options: bitwise libxml2 parser options (libxml2.XML_PARSE_*)
        catalog: url of a local XML catalog to use.  If None, parser uses system default (/etc/xml/catalog)
        """
        
        self.validate = validate
        self.options = options
        self.catalog = catalog
        self._v_errors = []
        libxml2.lineNumbersDefault(1)

    def parseErrorHandler(self, data, msg, severity, *args):
        e = libxml2.lastError()
        self._v_errors.append( (e.line(), msg) )

    def getErrors(self):
        """
        Return the errors collected while parsing
        """
        return self._v_errors

    def _doParse(self, parser):
        
        # Set requested options
        if self.options:
            parser.ctxtUseOptions(self.options)
        if self.catalog:
            parser.addLocalCatalog(catalog)

        self._v_errors = []
        parser.setErrorHandler(self.parseErrorHandler, None)

        r = parser.parseDocument()
        self._v_errors.sort(lambda x, y: cmp(x[0], y[0]))

        doc = parser.doc()
        del parser

        if r == 0 and len(self._v_errors) == 0:
            return doc
        else:
            doc.freeDoc()
            msg = '\n'.join(['Line %d: %s' % (line, error) for line, error in self._v_errors])
            raise XMLParserError, "Error: could not parse document: %s" % msg

    def parseString(self, content):
        """
        Parse string content into xmlDoc object

        Returns the document object if successful and raises XMLParserError otherwise
        NOTE: returned object MUST be freed with .freeDoc() method
        """
        #import pdb; pdb.set_trace()
        if type(content) is unicode:
            content = content.encode('utf-8')
        
        try:
            parser = libxml2.createMemoryParserCtxt(content, len(content))
        except libxml2.parserError:
            raise XMLParserError, "Error: could not parse document"

        return self._doParse(parser)

    def parseUrl(self, url):
        """
        Retrieve and parse the document at the provided URL.

        Returns the document object if successful and raises XMLParserError otherwise
        NOTE: returned object MUST be freed with .freeDoc() method

        Note: Any specified catalog will only be used to resolve entities internal
        to the document, not the url passed-in
        """
        try:
            parser = libxml2.createFileParserCtxt(url)
        except libxml2.parserError:
            raise XMLParserError, "Error: could not parse document"

        return self._doParse(parser)

def parseString(content):
    """
    Convenience function to parse string with sensible default options. Private: do not use.
    """
    parser = XMLParser(options=PARSER_OPTIONS)
    doc = parser.parseString(content)
    return doc

def parseUrl(url):
    """
    Convenience function to parse file with sensible default options. Private: do not use.
    """
    parser = XMLParser(options=PARSER_OPTIONS)
    doc = parser.parseUrl(url)
    return doc
        
def normalize(content):
    """
    Expanding entities and recode in UTF-8. Public.
    'content' is a string of the XML document to be normalized.
    """
    doc = parseString(content)
    result = doc.serialize(encoding='utf-8')
    doc.freeDoc()
    return result

#_relaxngdocs = {}  # already-compiled relaxng validators
_urlmaps = {}
_urlmaps["http://cnx.rice.edu/technology/cnxml/schema/rng/0.6/cnxml.rng"] = "/usr/share/xml/cnxml/schema/rng/0.6/cnxml-jing.rng"
def validate(content, url="http://cnx.rice.edu/technology/cnxml/schema/rng/0.6/cnxml.rng"): 
    """
    Convenience function for validating content. Public.
    'content' is a string of the XML document to be validated.
    'url' is a location of a RelaxNG schema to validate with

    Returns a list of (linenumber, error) tuples
    """
    if type(content) is unicode:
        content = content.encode('utf-8')

    schemaloc = _urlmaps.get(url, url)
    try:
        tmpfile = NamedTemporaryFile() # doesn't take stdin, so make a file
        tmpfile.write(content)
        tmpfile.flush()
        tmploc = tmpfile.name
        
        # A better way might perhaps be to wrap Jing with JCC
        # (http://pypi.python.org/pypi/JCC/) and be able to call directly through Python.
        # We might even be able to hold onto an open validator object that way
        # (creating the validator object takes much longer than validating, generally.)
        process = Popen(["java", "-jar", JINGJARPATH, schemaloc, tmploc], stdout=PIPE)
        process.wait()
        result = process.stdout.read()
    finally:
        tmpfile.close()  # deletes file
        
    
    result = result.strip()
    retlist = []
    if result:
        for l in result.split('\n'):
            parts = l.split(':')
            #file = parts[0]
            line = parts[1]
            
            try:
                line = str(int(line))
                #char = parts[2]  # throwing this away at the moment
                mesg = ':'.join(parts[3:])
            except:
                # not a line number, so use the whole thing
                line = 0
                mesg = l
                
                # known specific exceptions
                if mesg == 'fatal: exception "java.io.IOException" thrown: Stream closed.':
                    mesg = "DOCTYPE declaration not allowed."

            retlist.append((line,mesg))
    return retlist

    ## With lxml (using libxml2)
    ## see http://codespeak.net/lxml/validation.html#relaxng
    #relaxng_doc = _relaxngdocs.get(url, None)
    #if not relaxng_doc:  # store parsed validator doc if we don't have it already to save time
        #relaxng_doc  = etree.parse(url)
        #_relaxngdocs[url] = relaxng_doc
    ## we don't store the RelaxNG parser, because it has a stateful error log (see below), and we can't
    ## guarantee a shared obj wouldn't wrongly share error log entries in multi-thread situation
    #relaxng = etree.RelaxNG(relaxng_doc)
    
    #try:
        #doc = etree.parse(StringIO(content))  # TODO: introspect for doc version to automatically get schema?
    #except etree.XMLSyntaxError, e:
        #mes = str(e)   # like: 'line 3: Opening and ending tag mismatch: b line 1 and c'
        ## ad hoc parsing...
        #sepidx = mes.find(':')
        #line = mes[5:sepidx]
        #message = mes[sepidx+2:]
        #return [(line, message)]
    
    #success = relaxng.validate(doc)
    #if not success:
        #return [(x.line, x.message) for x in relaxng.error_log]
    #return []

def _quoteParam(param):
    if type(param) == type(0):
        return "%d" % param
    else:
        return "'%s'" % param
      

def transform(content, stylesheet, **params):
    """
    Perform an XSLT transformation on the provided content. Public.

    content: XML document string
    stylesheet: URL of XSLT stylesheet
    params: any other keyword arguments will be passed in as XSLT parameters
    """

    xsltlog.debug("XSL Transform: %s (%s)" % (stylesheet, params))

    try:
        doc = parseString(content)
        result = xsltPipeline(doc, [stylesheet], **params)
        doc.freeDoc()
    except libxml2.parserError, e:
        raise XMLError, e

    return result


def xsltPipeline(doc, stylesheets, **params):
    """
    Perform a series of XSLT transformation on the given document. Public.

    doc: an XML document
    stylesheets: list of XSLT stylesheet URLs
    params: any other keyword arguments will be passed in as XSLT parameters
    """
    xsltlog.debug("XSL Pipeline: %s (%s)" % (stylesheets, params))

    # libxslt requires parameters to be quoted
    for key in params.keys():
        params[key] = _quoteParam(params[key])

    # If pipeline is empty just serialize doc
    if not len(stylesheets):
        return doc.serialize()

    source = doc
    style = None
    for s in stylesheets:
        # Free stylesheet from previous loop iteration.  We do this
        # here so that the last stylesheet doesn't get freed until
        # after its used to  serialize the result
        if style is not None:
            style.freeStylesheet()

        styledoc = parseUrl(s)
        style = libxslt.parseStylesheetDoc(styledoc)  # TODO: keep stylesheet around
        if not style:
            raise XSLTError, "Error parsing %s" % s
        output = style.applyStylesheet(source, params)
        
        # Don't free the original source doc
        if source != doc:
            source.freeDoc()
        source = output

    try:
        # Use the last stylesheet to serialize the output (part of the transform may have to do with
        # serialization of the document)
        result = style.saveResultToString(output)
    except SystemError:
        # might fail on empty files, so use alternate serialization
        result = output.serialize()

    style.freeStylesheet()
    output.freeDoc()
    
    return result


def listDocNamespaces(doc):
    """Return a list of namespaces declared in the document. Public."""
    # XXX: There really ought to be a better way to get the namespaces
    # from a parsed document
    # TODO: this requres a parsed doc, which we want to be rid of.
    ns = {}
    for node in doc.walk_depth_first():
        if node.type == 'element':
            try:
                n = node.ns()
            except libxml2.treeError:
                continue
            if n:
                ns[n.content] = 1
                
            for n in nodeNamespaces(node):
                ns[n.content] = 1

    namespaces = ns.keys()
    namespaces.sort()

    return namespaces

def nodeNamespaces(node):
    """Generator to iterate over namespaces defined on a node"""
    n = node.nsDefs()
    while n:
        yield n
        n = n.next

def _normalizeFile(filename):
    f = open(filename)
    content = f.read()
    f.close()

    return normalize(content)


def _validateFile(filename):
    f = open(filename)
    content = f.read()
    f.close()

    return validate(content)


def _transformFile(ssFile, contentFile):
        
    f = open(contentFile)
    content = f.read()
    f.close()

    return transform(content, ssFile)
    
    
if __name__ == "__main__":
    import sys

    if (len(sys.argv) < 2):
        print "Usage: XMLService [validate|normalize|transform] [SS] FILE"
        sys.exit(-1);

    operation = sys.argv[1]
    if operation == 'validate':
        result = _validateFile(sys.argv[2])
    elif operation == 'transform':
        result = _transformFile(sys.argv[2], sys.argv[3])
    elif operation == 'normalize':
        result = _normalizeFile(sys.argv[2])
    else:
        print "Usage: XMLService [validate|normalize|transform] [SS] FILE"
        sys.exit(-1);

    print result

