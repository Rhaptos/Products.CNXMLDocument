
from Products.CMFCore.utils import getToolByName

def reorderPredicate(context):
    """ set the cnxml predicate to the top of the list """
    if context.readDataFile('cnxmldocument-reorder.txt'):
        return
    portal = context.getSite()
    registry = getToolByName(portal, 'content_type_registry')
    registry.reorderPredicate('cnxml', 0)
