# -*- coding: utf-8 -*-
from collective.taxonomy.browser import TaxonomyView
from Products.Five import BrowserView


class FacetedGeoJSONPopup(BrowserView):
    def popup(self, brain, short_names=["applications"]):
        template = "<a href='{0}' title='{1}'>" "<div>{1} <ul>{2}</ul></div></a>"
        obj = brain.getObject()
        tax_view = TaxonomyView(obj, obj.REQUEST)
        taxonomies = tax_view.taxonomiesForContext(short_names=short_names)
        taxonomies.sort()
        taxonomy = "".join(["<li>{}</li>".format(tax) for tax in taxonomies])
        return template.format(brain.getURL(), brain.Title, taxonomy)
