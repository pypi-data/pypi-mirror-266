.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

====================
visaplan.plone.tools
====================

General tools modules for Plone.

We don't claim ultimate Plone wisdom (yet);
this package is one of the parts a big monolithic classic Zope product
was split into.

It is part of the footing of the "Unitracc family" of Plone sites
which are maintained by visaplan GmbH, Bochum, Germany.

Some modules of this package might still contain some resources
(e.g. type names)
which are specific to our "Unitracc family" of sites;
this is likely to change in future releases.


Features
--------

This add-on can be seen in action at the following sites:

- https://www.unitracc.de
- https://www.unitracc.com

Modules in version 1.1.4+:

- ``attools`` module

  several tools for Archetypes-based content

- ``brains`` module

  currently one ``make_collector`` function, e.g. for address fields

- ``cfg`` module

  Read "product" configuration, and detect development mode

- ``context`` module

  Several tools for processing the request.
  Some need some modernization ...

- ``forms`` module

  Several tools for forms

- ``functions`` module

  Some functions, e.g. ``is_uid_shaped``

- ``indexes`` module (new in v1.1.4) 

  - Function ``getSortableTitle`` for title conversion.

    This converts umlauts etc. to sort them
    as equal to their corresponding base vocals,
    according to German lexical usage.

- ``log`` module

  Automatically named loggers

- ``mock`` module

  - a few small classes for use in doctests

  - the same module as ``visaplan.tools.mock``

- ``mock_cfg`` module

  A rudimentary mock module for ``cfg``

- ``search`` module

  A few functions to support creation of ZODB catalog search queries
  (quite proprietary, I'm afraid; might go away in future versions)

- ``setup`` module (since v1.1)

  Functions for use in migration scripts

- ``zcmlgen`` module (since v1.1.1)

  - Generates ``configure.zcml`` files, if

    - changes are detected, and

    - development mode is active, and

    - the source is in an development package.

- ``decorators`` module (since v1.1.6)

  - ``@returns_json``:

    Wraps the function call and returns the JSON_-encoded result,
    including HTTP headers.

    Uses simplejson_ if available.

Documentation
-------------

Sorry, we don't have real user documentation yet.

Most functions are documented by doctests, anyway;
it helps to understand some German.


Installation
------------

Since ``visaplan.plone.tools`` is a package for Plone instances,
it is not normally installed using ``pip``;
instead, install it by adding it to your buildout::

    [buildout]

    ...

    eggs =
        visaplan.plone.tools


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/visaplan/plone.tools/issues
- Source Code: https://github.com/visaplan/plone.tools


Support
-------

If you are having issues, please let us know;
please use the `issue tracker`_ mentioned above.


License
-------

The project is licensed under the GPLv2.

.. _`issue tracker`: https://github.com/visaplan/plone.tools/issues
.. _JSON: https://json.org/
.. _simplejson: https://pypi.org/project/simplejson

.. vim: tw=79 cc=+1 sw=4 sts=4 si et


Contributors
============

- Tobias Herp, tobias.herp@visaplan.com


Changelog
=========


2.0.0 (unreleased)
------------------

- Breaking changes:

  - ``forms.tryagain_url``:

    - all options (which are all arguments except the request) will `need to` be given by name
      (which is possible and `recommended already`).


1.2.2 (unreleased)
------------------

Improvements:

- ``setup`` module:

  - If the ``reindex`` function, which was created by the ``make_reindexer`` factory,
    was given an object both by `brain` and by itself, it compared those two by identity,
    which wouldn't ever match.  Now checking for equality.

  - New function ``clone_tree`` (from release 1.2.0) now works recursively

  - When ``clone_tree`` moves objects from one folder to another, it tries to preserve a useful order;
    both functions ``_clone_tree_inner`` and ``_move_objects`` use the new helper ``apply_move_order_options``
    to inject a ``sort_on`` key into the query.

- ``context`` module:

  - ``getMessenger`` factory function: creates a `message` function
    which doesn't require (nor accept) a `context` argument

  - `make_permissionChecker` doesn't require the ``checkperm``
    adapter any more to be useful

  - `make_userdetector` doesn't require the ``auth``
    adapter any more to be useful

- Working doctests for ``search`` module

New Features:

- New factory function ``context.getMessenger``:

  creates a `message` function which doesn't require
  (nor accept) a `context` argument

- New function ``setup.safe_context_id``

- New function ``search.normalizeQueryString`` (unicode, asterisks)

Bugfixes:

- ``context.message``: The default `mapping` is `None` now!

Requirements:

- visaplan.plone.infohubs_ 1.1.1+

[tobiasherp]


1.2.1 (skipped)
---------------


1.2.0 (2020-05-13)
------------------

New utilities:

- ``setup`` module:

  - New function ``clone_tree``, using
  - function factory ``make_object_getter``
    and
  - function factory ``make_subfolder_creator``

  Both factories have overlapping functionality and might become unified in a future version;
  their initial purposes were:

  ``make_object_getter`` creates a function (usually called ``get_object``)
  which tries to *find* a (possibly moved and/or renamed) object,
  and then is able to apply a few changes;

  ``make_subfolder_creator`` creates a function (usually called ``new_folder``)
  which creates a new *folder* (unless already present),
  and then is able to apply a few changes.

[tobiasherp]


1.1.6 (2019-11-27)
------------------

New modules:

- ``decorators`` module:

  - ``@returns_json``
    (uses simplejson_ if available)

New utilities:

- ``context`` module:

  - function factory ``make_timeformatter``

Bugfixes:

- Typo in README corrected.

[tobiasherp]


1.1.5 (2019-07-18)
------------------

Bugfixes:

- ``getConfiguration`` might fail; in such cases, log a warning and use the default
- Missing requirements:

  - visaplan.kitchen_

[tobiasherp]


1.1.4 (2019-05-09)
------------------

- ``indexes`` module added:

  - Function ``getSortableTitle`` for title conversion.

    This converts umlauts etc. to sort them
    as equal to their corresponding base vocals,
    according to German lexical usage.

- ``attools`` module:

  - New function ``notifyedit(context)``

- ``forms`` module:

  - ``tryagain_url`` function supports ``var_items`` argument

  - bugfix for ``make_input`` function (suppression of ``type`` attribute)

- ``zcmlgen`` module:

  - changes detection improved to explicitly ignore added/removed blank lines

- ``context`` module:

  - new functions ``message`` and ``getbrain``,
    as replacement for some adapters named alike

[tobiasherp]


1.1.3 (2019-01-29)
------------------

- ``setup.make_renamer()``: generated ``rename`` function improved:
  existing positional options default to ``None``; instead of ``uid``,
  ``o`` (object) or ``brain`` can be specified (by name).

- ``setup.make_query_extractor()``, generated ``extract_query`` function improved:
  don't convert a ``Language`` string to a list if it's value is ``all``

- ``zcmlgen`` module:

  - Bugfix for changes detection

  - If changes are found but disallowed (non-development setup),
    and if ``sys.stdout`` is connected to a terminal,
    start the debugger

  [tobiasherp]


1.1.2 (2018-11-21)
------------------

- Corrections for the documentation

- (currently) unused dependencies removed
  [tobiasherp]


1.1.1 (2018-09-27)
------------------

- ``zcmlgen`` module added:

  - Generates ``configure.zcml`` files, if

    - changes are detected (*buggy*; see v1.1.3), and

    - development mode is active, and

    - the source is in a development package.


1.1 (2018-09-17)
----------------

- ``attools`` module added:

  - a brown bag of tools for Archetypes

- ``brains`` module added:

  - ``make_collector``, e.g. for address fields

- ``forms`` module added:

  - a brown bag of modules to support forms in a Zope/Plone system

- ``mock`` module added:

  - a few small classes for use in doctests

  - the same module as visaplan.tools_ .mock

- ``mock_cfg`` module added:

  - accompanies ``cfg``, for testing only

- ``search`` module added:

  - tools for creation of catalog queries

- ``setup`` module added: functions for use in migration scripts

- Module changes:

  - ``context`` module:

    - new function ``decorated_tool``

  - ``functions`` module:

    - new function ``looksLikeAUID`` (for historical reasons)


1.0 (2018-07-11)
----------------

- Initial release.
  [tobiasherp]

.. _simplejson: https://pypi.org/project/simplejson
.. _visaplan.kitchen: https://pypi.org/project/visaplan.kitchen
.. _visaplan.plone.infohubs: https://pypi.org/project/visaplan.plone.infohubs
.. _visaplan.tools: https://pypi.org/project/visaplan.tools

