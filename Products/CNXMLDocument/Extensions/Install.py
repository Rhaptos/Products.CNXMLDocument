__version__ = "0.1"

from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.CNXMLDocument import PortalCNXMLFile, product_globals
from cStringIO import StringIO
import string

def setProp(tool, prop, value):
    #log("Setting property [%s , %s]" % (prop, value))
    try:
        tool._delProperty(prop)
    except: pass
    tool._setProperty(prop, value)

def install(self):
    """Register PortalCNXMLFile with the necessary tools"""
    out = StringIO()

    # Setup the types tool
    typestool = getToolByName(self, 'portal_types')
    for t in PortalCNXMLFile.factory_type_information:
        if t['id'] not in typestool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), t)
            typestool._setObject(t['id'], cfm)
            out.write('Registered with the types tool\n')
        else:
            out.write('Object "%s" already existed in the types tool\n' % (
                t['id']))

    # Setup the skins
    skinstool = getToolByName(self, 'portal_skins')
    if 'CNXMLFile' not in skinstool.objectIds():
        # We need to add Filesystem Directory Views for any directories
        # in our skins/ directory.  These directories should already be
        # configured.
        addDirectoryViews(skinstool, 'skins', product_globals)
        out.write("Added 'CNXMLFile' directory view to portal_skins\n")

    # Now we need to go through the skin configurations and insert
    # 'PortalCNXMLFile' into the configurations.  Preferably, this
    # should be right before where 'custom' is placed.  Otherwise, we
    # append it to the end.
    skins = skinstool.getSkinSelections()
    for skin in skins:
        path = skinstool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        if 'CNXMLFile' not in path:
            try: path.insert(path.index('custom')+1, 'CNXMLFile')
            except ValueError:
                path.append('CNXMLFile')
                
            path = string.join(path, ', ')
            # addSkinSelection will replace existing skins as well.
            skinstool.addSkinSelection(skin, path)
            out.write("Added 'CNXMLFile' to %s skin\n" % skin)
        else:
            out.write("Skipping %s skin, 'CNXMLFile' is already set up\n" % (
                skin))

    # Register with content_type_registry
    out.write("Registering with content_type_registry\n")
    registry = self.content_type_registry
    if registry.getPredicate('cnxml'):
        registry.removePredicate('cnxml')
    registry.addPredicate('cnxml', 'extension')
    pred = registry.predicates['cnxml'][0]
    pred.edit('cnxml')
    registry.assignTypeName('cnxml', 'CNXML Document')
    registry.reorderPredicate('cnxml', 0)

    # Make workflow go away
    out.write("Making workflow empty\n")
    wf_tool = getToolByName(self,'portal_workflow')
    wf_tool.setChainForPortalTypes(['CNXML File'],'')

#    PLONE2.5 NOTE: I don't think this is used anymore.  Should all be FormController now.
#    # Setting up forms tool stuff
#    out.write("Setting up form validation\n")
#    pr_tool = getToolByName(self, 'portal_properties')
#    setProp(pr_tool.form_properties, 'cnxml_edit_form', 'validate_cnxml')
#    setProp(pr_tool.navigation_properties, 'default.cnxml_edit_form.success', 'cnxml_edit_form')
#    setProp(pr_tool.navigation_properties, 'default.cnxml_edit_form.failure', 'cnxml_edit_form')


    return out.getvalue()

