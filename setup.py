from setuptools import setup, find_packages
import os

version = '1.8'
maintainer = 'Mathias Leimgruber'
tests_require = [
    'ftw.testing',
    'ftw.tabbedview',
    'ftw.table',
    'plone.testing',
    'plone.app.testing',
    ]

setup(name='ftw.usermanagement',
      version=version,
      description='An advanced view for managing users in plone.',
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        ],

      keywords='ftw usermanagement user management view plone',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.usermanagement/',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'ftw.table',
        'ftw.tabbedview',
        'plone.principalsource',
        'collective.js.jqueryui',
        'collective.js.ui.multiselect',
        # -*- Extra requirements: -*-
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points='''
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      ''',
      )
