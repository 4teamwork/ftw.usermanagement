ftw.usermanagement
==================

This package allows users to easily manage users and groups through
a new view without having plone's manage portal permission. This is useful
when the person who manages users and groups should have full manager access
to the site.

If the user has the permission "Manage users", a new action is displayed in
the user menu, giving him the ability to list and modify users and groups.


Features
--------

- Manage users

  - List users
  - Assign users to groups
  - Add users
  - Delete users
  - Reset password of a user and send a notification

- Manage groups

  - List groups
  - Add groups
  - Delete groups


Usage
-----

If you are using ``zc.buildout`` and the ``plone.recipe.zope2instance``
recipe to manage your project, you can do this:

- Add ``ftw.usermanagement`` to the list of eggs to install, e.g.:

::

    [instance]
    ...
    eggs =
        ...
        ftw.usermanagement

- Re-run buildout, e.g. with:

::

    $ ./bin/buildout

- Install the generic setup profile.

- Grant chosen users the ``zope2.ManageUsers`` ("Manage users") permission.

Compatibility
=============

Plone 4.2

.. image:: https://jenkins.4teamwork.ch/job/ftw.usermanagement-master-test-plone-4.2.x.cfg/badge/icon
   :target: https://jenkins.4teamwork.ch/job/ftw.usermanagement-master-test-plone-4.2.x.cfg

Plone 4.3

.. image:: https://jenkins.4teamwork.ch/job/ftw.usermanagement-master-test-plone-4.3.x.cfg/badge/icon
   :target: https://jenkins.4teamwork.ch/job/ftw.usermanagement-master-test-plone-4.3.x.cfg


Links
=====

- Github: https://github.com/4teamwork/ftw.usermanagement
- Issues: https://github.com/4teamwork/ftw.usermanagement/issues
- Pypi: http://pypi.python.org/pypi/ftw.usermanagement
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.usermanagement


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.usermanagement`` is licensed under GNU General Public License, version 2.
