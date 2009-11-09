"""
A CNXML version recognizer.

Author: J Cameron Cooper (jccooper@rice.edu/jccooper@gmail.com)
Copyright (C) 2008, 2009 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""
import xml.parsers.expat

CHUNK_SIZE = 400

class Recognizer:
    """Class to do CNXML version recognition.
    Implmented with Python expat.
    Construct with 'doctext' as text of CNXML document, and call 'getVersion'.
    You probably don't need to keep the class around, so call anonymously::
      Recognizer(text).getVersion()
    """
    
    # setup
    def __init__(self, doctext):
        self._doctext = doctext
        self.version = None
        
        # expat parsers are only for a single use, apparently, so create them on the fly
        self.p = xml.parsers.expat.ParserCreate()
        self.p.StartElementHandler     = self.start_element
        #self.p.EndElementHandler       = self.end_element
        #self.p.CharacterDataHandler    = self.char_data
        self.p.StartDoctypeDeclHandler = self.start_doctype
        #self.p.EndDoctypeDeclHandler   = self.end_doctype
    
    # handler functions
    def start_element(self, name, attrs):
        if name == "document":
            if attrs.has_key('cnxml-version'):
                self.version = attrs['cnxml-version']
    
    #def end_element(self, name):
        #print 'End element:', name
    
    #def char_data(self, data):
        #print 'Character data:', repr(data)
    
    def start_doctype(self, doctypeName, systemId, publicId, has_internal_subset):
        if publicId.find("CNXML") != -1:
            # publicId like "-//CNX//DTD CNXML 0.5//EN"
            dtdstr = publicId.split("//")[2]
            dtdstr = dtdstr.split()[2]
            self.version = dtdstr
    
    #def end_doctype(self):
        #print 'End doctype:'
    
    # do the parsing
    def getVersion(self):
        """Attempt to recognize the version of a CNXML document.
        Specifically focused on 0.6+, but we also try to detect 0.5/0.4 by doctype.
        Will return strings like "0.5" or "0.6". None if not detectable.
        """
        # expat can parse in chunks; do this so we only handle as much as we need to,
        # which is probably only one chunk
        doctext = self._doctext
        startat = 0
        endidx = len(doctext)
        while not self.version and startat < endidx:
            upto = startat + CHUNK_SIZE
            chunk = doctext[startat:upto]
            if type(chunk) is unicode:  # expat should be able to handle unicode, but chokes, so go old-style
                chunk = chunk.encode('utf-8')
            
            try:
                self.p.Parse(chunk)
            except xml.parsers.expat.ExpatError:
                return None
            startat = upto
        return self.version
