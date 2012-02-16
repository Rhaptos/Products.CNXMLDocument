from Products.Five import BrowserView

from Products.CNXMLDocument import CNXML_RENDER_XSL, CNXML_SEARCHABLE_XSL
from Products.CNXMLDocument import XMLService
from Products.CNXMLDocument.XMLService import XMLError


def rendercnxml(source, prestyles=()):

    stylesheets = list(prestyles)
    stylesheets.append(CNXML_RENDER_XSL)
    
    params = {}
    params['wrapper'] = 0
    
    doc = XMLService.parseString(source)
    result = XMLService.xsltPipeline(doc, stylesheets, **params)
    return result


class CNXMLComponents(BrowserView):
    """Component Architecture view class for components of a CNXML document."""
    #implements(ICNXMLComponents)

    def abstract(self):
        """The rendered abstract/summary text of content, by itself.
        """
        context = self.context
        source = getattr(context, 'getRawAbstract', None)
        source = source and source() or context.abstract
        if source:
            source = """<md:abstract xmlns="http://cnx.rice.edu/cnxml"
                                    xmlns:bib="http://bibtexml.sf.net/"
                                    xmlns:m="http://www.w3.org/1998/Math/MathML"
                                    xmlns:md="http://cnx.rice.edu/mdml"
                                    xmlns:q="http://cnx.rice.edu/qml/1.0">%s</md:abstract>""" % source
            return rendercnxml(source)
        return ''
      
    def abstract_text(self):
        """The rendered abstract/summary text of content, by itself, stripped of markup.
        """
        context = self.context
        source = getattr(context, 'getRawAbstract', None)
        source = source and source() or context.abstract
        if source:
            source = """<md:abstract xmlns="http://cnx.rice.edu/cnxml"
                                    xmlns:bib="http://bibtexml.sf.net/"
                                    xmlns:m="http://www.w3.org/1998/Math/MathML"
                                    xmlns:md="http://cnx.rice.edu/mdml"
                                    xmlns:q="http://cnx.rice.edu/qml/1.0">%s</md:abstract>""" % source
	    doc = XMLService.parseString(source)
	    result = XMLService.xsltPipeline(doc, CNXML_SEARCHABLE_XSL)
	    return result
        return ''
      
    def body(self):
        """The body text of a CNXML document, by itself.
        Mostly borrowed (without too much analysis) from cnx_overrides/cnxml_transform
        """
        context = self.context
        kw = {}
        kw.update(context.getCourseParameters())  # TODO: not used?
        
        source = context.normalize()  # .source() sets headers, which we don't want
        
        ### cnx_override for CNXML < 0.5 ###
        # If old CNXML Document
        prestyles = []
        doctype = getattr(context, 'doctype', None)
        if doctype and doctype.find('0.5') == -1:
            from Products.CNXMLDocument import CNXML_UPGRADE_XSL
            prestyles = [CNXML_UPGRADE_XSL]
        ### /cnx_override
        
        return rendercnxml(source, prestyles=prestyles)
