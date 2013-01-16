from setuptools import setup, find_packages

PACKAGE = 'TestManager'
version = '0.3.0'

setup(name='TracTestManager',
      version=version,
      description="TestManager Plugin for TRAC",
      long_description="""\
      TestManager Plugin for TRAC""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='trac tests testcases',
      author='Otto Hockel',
      author_email='otto.hockel@inquant.de',
      url='www.inquant.de',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      package_data={'tractestmanager' : ['templates/*.html', 'htdocs/js/*.js', 'htdocs/css/*.css']},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={'trac.plugins': '%s = tractestmanager' % PACKAGE},
      )
