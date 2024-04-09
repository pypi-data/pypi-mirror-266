from distutils.core import setup

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(
  name = 'compteur',
  packages = ['compteur'],
  version = '1.1',
  license='MIT',
  description = 'Count how many time errors occur',
  long_description = long_description,
  long_description_content_type = "text/markdown",
  author = 'OlivierProTips',
  url = 'https://github.com/OlivierProTips/compteur',
  keywords = ['Compteur', 'error', 'count', 'track'],
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
