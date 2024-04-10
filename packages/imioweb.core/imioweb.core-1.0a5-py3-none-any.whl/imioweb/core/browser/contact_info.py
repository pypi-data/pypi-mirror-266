# -*- coding: utf-8 -*-

from plone.autoform import directives
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget
from Products.CMFPlone.browser.contact_info import ContactForm as BaseContactForm
from Products.CMFPlone.browser.interfaces import IContactForm as IBaseContactForm
from zope import schema


class IContactForm(IBaseContactForm):

    directives.widget("recaptcha", ReCaptchaFieldWidget)
    recaptcha = schema.TextLine(title="ReCaptcha", required=False)


class ContactForm(BaseContactForm):

    schema = IContactForm
