"""
Zope 3 Component Architecture view(s) for CNXMLDocument, including general MDML.

Author: J. Cameron Cooper (jccooper@rice.edu)
Copyright (C) 2009 Rice University. All rights reserved.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from Acquisition import aq_inner

MD_FETCH = 'getMetadata'

class MetadataView(BrowserView):
    """View class for Metadata, for various types of object. Relies on similar interface
    for getMetadata."""
    def set_repository(self, repository):
        self.repository = repository
    
    def metadata(self):
        context = aq_inner(self.context)
        parent = context.aq_parent
        getMetadata = getattr(parent, MD_FETCH, getattr(context, MD_FETCH, lambda:None))
        retval = getMetadata()
        
        repos = getattr(self, 'repository', None)
        if repos:
            oldrepos = retval['repository']
            retval['repository'] = repos
            if retval['url'].startswith(oldrepos):
                retval['url'] =  retval['url'].replace(oldrepos, repos)
        
        # actor/role refactoring: our content stores this nicely in role categories, but
        # we need a global list of actors for the MDML format
        mtool = getToolByName(self, 'portal_membership')
        uniqs = set()
        for r in ['authors', 'maintainers', 'licensors', 'editors', 'translators']:
            rolelist = retval.get(r, [])
            for uid in rolelist:
                uniqs.add(uid)
        
        actors = []
        for uid in uniqs:
            m = mtool.getMemberById(uid)
            mdata = {}
            mdata['id'] = uid
            mdata['shortname'] = m.getProperty('shortname')
            mdata['firstname'] = m.getProperty('firstname')
            mdata['surname'] = m.getProperty('surname')
            mdata['fullname'] = m.getProperty('fullname')
            mdata['email'] = m.getProperty('email')
            mdata['account_type'] = m.getProperty('account_type')
            actors.append(mdata)
        retval['actors'] = actors
        
        return retval