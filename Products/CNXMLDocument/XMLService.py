#!/usr/bin/env python
"""
XMLService - wrapper around libxml2 using lxml to provide basic XML services

Author: Brent Hendricks, Ross Reedstrom
(C) 2005,2012 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import os
from lxml import etree
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from cStringIO import StringIO

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

# Default options for xml parsing

PARSER_OPTIONS={'load_dtd':True,
                'resolve_entities':True,
                'no_network':True,
                'attribute_defaults':False,
                }



def parseString(content):
    """
    Convenience function to parse string with sensible default options. Private: do not use.
    """
    try:
        parser = etree.XMLParser(**PARSER_OPTIONS)
        doc = etree.ElementTree(etree.fromstring(content, parser=parser))
        return doc
    except etree.XMLSyntaxError, e:
        raise XMLParserError, e

def parseUrl(url):
    """
    Convenience function to parse file with sensible default options. Private: do not use.
    """
    try:
        parser = etree.XMLParser(**PARSER_OPTIONS)
        doc = etree.parse(url, parser=parser)
        return doc
    except etree.XMLSyntaxError, e:
        raise XMLParserError, e
        
def normalize(content):
    """
    Expanding entities and recode in UTF-8. Public.
    'content' is a string of the XML document to be normalized.
    """
    doc = parseString(content)
    result = etree.tostring(doc.getroot())
    return result


#_relaxngdocs = {}  # already-compiled relaxng validators
_urlmaps = {}
_urlmaps["http://cnx.rice.edu/technology/cnxml/schema/rng/0.6/cnxml.rng"] = "/usr/share/xml/cnxml/schema/rng/0.6/cnxml-jing.rng"
_urlmaps["http://cnx.rice.edu/technology/cnxml/schema/rng/0.7/cnxml.rng"] = "/usr/share/xml/cnxml/schema/rng/0.7/cnxml-jing.rng"
_urlmaps["http://cnx.rice.edu/technology/cnxml/schema/rng/0.7/cnxml-fragment.rng"] = "/usr/share/xml/cnxml/schema/rng/0.7/cnxml-fragment-jing.rng"

def validate(content, url="http://cnx.rice.edu/technology/cnxml/schema/rng/0.7/cnxml.rng"): 
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
    except etree.XMLSyntaxError, e:
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

    for k,v in params.items():
        if type(v) in [int, long, float]:
            params[k]='%s' % str(v)
        else:
            params[k]='"%s"' % str(v)

    # If pipeline is empty just serialize doc
    if not len(stylesheets):
        return etree.tostring(doc)

    source = doc
    style = None
    for s in stylesheets:
        styledoc = parseUrl(s)
        style = etree.XSLT(styledoc)# TODO: keep stylesheet around
        if not style:
            raise XSLTError, "Error parsing %s" % s
        output = style(source, **params)
        source = output

    result = str(output)
    return result


def listDocNamespaces(doc):
    """Return a list of namespaces declared in the document. Public."""
    # XXX: There really ought to be a better way to get the namespaces
    # from a parsed document
    # TODO: this requires a parsed doc, which we want to be rid of.
    ns = {}
    for node in doc.iter():
        ns.update({}.fromkeys(node.nsmap.values()))

    namespaces = ns.keys()
    namespaces.sort()

    return namespaces

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

