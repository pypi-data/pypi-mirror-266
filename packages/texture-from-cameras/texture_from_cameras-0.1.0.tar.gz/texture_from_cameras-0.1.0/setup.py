from setuptools import find_packages
from distutils.core import setup
setup(
  name = 'texture_from_cameras',
  packages=find_packages('src'),
  package_dir={'': 'src'},
  version = '0.1.0',      # Start with a small number and increase it with every change you make
  license='GPL-3.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = '',   # Give a short description about your library
  author = 'Leone Jesus',
  author_email = 'leone.jesus@fieb.org',
  url = 'https://github.com/leonejesus/texture_from_cameras',
  download_url = 'https://github.com/leonejesus/texture_from_cameras/archive/refs/tags/v0.1.0.tar.gz',
  keywords = ['SfM', 'MeshLab', 'Texturing'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pymeshlab==2022.2',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)