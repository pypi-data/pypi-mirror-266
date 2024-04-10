# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import imioweb.core


class ImiowebCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(name="testing.zcml", package=imioweb.core)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "imioweb.core:default")


IMIOWEB_CORE_FIXTURE = ImiowebCoreLayer()


IMIOWEB_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIOWEB_CORE_FIXTURE,), name="ImiowebCoreLayer:IntegrationTesting"
)


IMIOWEB_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIOWEB_CORE_FIXTURE,), name="ImiowebCoreLayer:FunctionalTesting"
)


IMIOWEB_CORE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(IMIOWEB_CORE_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="ImiowebCoreLayer:AcceptanceTesting",
)
