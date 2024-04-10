# -*- coding: utf-8 -*- vim: tw=79 cc=+1 sw=4 sts=4 et si
"""
visaplan.plone.tools: attools: Archetypes-related tools (_at6)
"""

def can_be_html(field):
    # for use as a predicate for schema.filterFields
    # (see the Products.Archetypes.Schema.Schemata class):
    # for a field to match,
    # each predicate function must return something truish
    act = getattr(field, 'allowable_content_types', None)
    if act is None:
        return 0
    if not isinstance(act, (list, tuple)):
        return 0
    return 'text/html' in act

