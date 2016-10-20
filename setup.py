from setuptools import setup, find_packages
import os

version = '1.9.5'
maintainer = 'Mathias Leimgruber'
tests_require = [
    'ftw.builder',
    'ftw.tabbedview',
    'ftw.table',
    'ftw.testbrowser',
    'ftw.testing',
    'plone.app.testing',
    'plone.testing',
    ]

setup(name='ftw.usermanagement',
      version=version,
      description='An advanced view for managing users in plone.',
      long_description=open('README.rst').read() + '\n' + \
                       open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
          'Framework :: Plone',
          'Framework :: Plone :: 4.2',
          'Framework :: Plone :: 4.3',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],

      keywords='ftw usermanagement user management view plone',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.usermanagement',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'Plone',
          'collective.js.jqueryui',
          'collective.js.ui.multiselect',
          'ftw.tabbedview',
          'ftw.table',
          'ftw.upgrade >= 1.11.0',  # upgrade-step:directory support
          'plone.principalsource',
          'setuptools',
          ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points='''
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      ''',
      )
