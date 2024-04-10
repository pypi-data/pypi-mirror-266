# -*- coding: utf-8 -*-
from collective.taxonomy.interfaces import ITaxonomy
from imioweb.core.testing import IMIOWEB_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.schemaeditor.utils import FieldAddedEvent
from plone.schemaeditor.utils import IEditableSchema
from zope import schema
from zope.component import queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent

import unittest


class TestView(unittest.TestCase):
    layer = IMIOWEB_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_geojson_popup_view(self):
        applyProfile(self.portal, "collective.taxonomy:examples")
        utility = queryUtility(ITaxonomy, name="collective.taxonomy.test")
        document = api.content.create(
            container=self.portal, type="Document", id="document"
        )

        taxonomy_test = schema.Set(
            title="taxonomy_test",
            description="taxonomy description schema",
            required=False,
            value_type=schema.Choice(vocabulary="collective.taxonomy.test"),
        )
        portal_types = api.portal.get_tool("portal_types")
        fti = portal_types.get("Document")
        doc_schema = fti.lookupSchema()
        schemaeditor = IEditableSchema(doc_schema)
        schemaeditor.addField(taxonomy_test, name="taxonomy_test")
        notify(ObjectAddedEvent(taxonomy_test, doc_schema))
        notify(FieldAddedEvent(fti, taxonomy_test))

        simple_tax = [val for val in utility.data["en"].values()]
        document.taxonomy_test = set(simple_tax[0])

        brain_doc = api.content.find(portal_type="Document", id="document")[0]
        view = api.content.get_view(
            name="faceted-map-geojson-popup", context=self.portal, request=self.request
        )
        taxonomies = view.popup(brain_doc, short_names=["test"])
        self.assertEqual(
            taxonomies,
            "<a href='http://nohost/plone/document' title=''><div> <ul><li>Information Science</li></ul></div></a>",
        )
