from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='csscurrent',
  version='0.0.1',
  description='personal use for @aulte',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Aulte X',
  author_email='x@disgusting.cc',
  license='MIT', 
  classifiers=classifiers,
  keywords='csscurrent', 
  packages=find_packages(),
  install_requires=['requests', 'uuid'] 
)