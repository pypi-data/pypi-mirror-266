from setuptools import setup

__version__ = 'undefined'
exec(open('forgehg/version.py').read())

TOOL_DESCRIPTION = """ForgeHg enables an Allura installation to use the Mercurial
source code management system. Mercurial (Hg) is an open source distributed
version control system (DVCS) similar to git and written in Python.
"""

setup(name='ForgeHg',
      version=__version__,
      description="Mercurial (Hg) SCM support for Apache Allura",
      long_description=TOOL_DESCRIPTION,
      classifiers=[
        ## From http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: TurboGears',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
      ],
      keywords='Allura forge Mercurial Hg scm',
      author_email='dev@allura.apache.org',
      url='http://sourceforge.net/p/forgehg',
      license='GPLv2',
      packages=[
        'forgehg',
        'forgehg.model',
        'forgehg.templates'
      ],
      include_package_data=True,
      zip_safe=True,
      python_requires='>=3.7',
      install_requires=[
          # Restricting max version since mercurial is tightly integrated and changes often can break our code
          # See https://www.mercurial-scm.org/wiki/WhatsNew/ when testing upgrades and search for methods we use
          #  (although undocumented changes can frequently break our integration too)
          # Do manual testing also, especially making a merge request and merging it.  `test_merge` mocks way too much
          # Also, a newly created repo (hg init) has a .hg/requires file which might list new requirements:
          #   The hg repo services (not part of Allura; whatever is actually serving the repo) needs to be a new
          #   enough version to support these requirements.  You can test by editing a .hg/requires file on an existing
          #   repo (add in the new requirement lines) and see if the serving infrastructure can still serve it ok.
          #   See https://www.mercurial-scm.org/wiki/MissingRequirement
          #   And previously https://www.mercurial-scm.org/wiki/RequiresFile
          # 6.1.3 was latest version tested
          'mercurial < 6.2, >= 5.8',
          'six',
      ],
      entry_points="""
      [allura]
      Hg=forgehg.hg_main:ForgeHgApp

      [allura.timers]
      hg = forgehg.hg_main:hg_timers
      forgehg = forgehg.hg_main:forgehg_timers
      """,
      )
