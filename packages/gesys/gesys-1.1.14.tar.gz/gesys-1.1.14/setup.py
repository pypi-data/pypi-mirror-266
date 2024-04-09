from setuptools import setup, find_packages
import sys
from pathlib import Path

def readme():
  readme_path = str(Path(__file__).parent)+'/README.md'
  with open(readme_path, 'r') as f:
    return f.read()

version = '1.1.1'
if('version' in sys.argv):
  version = sys.argv[-1]
  sys.argv.remove(version)
  sys.argv.remove('version')

print(find_packages(exclude=['src', 'src.*']))
setup(
  name='gesys',
  version=version,
  package_dir={'gesys':'gesys'},
  author='Gesys',
  author_email='a.letyagin1@gmail.com',
  description='Control your computer with gestures.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/ArtemLetyagin/Gesys',
  packages=find_packages(exclude=['src', 'src.*']),
  install_requires=['opencv-python', 'onnxruntime', 'numpy'],
  classifiers=[
    'Programming Language :: Python :: 3.9',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='gesture gestures control',
  project_urls={
    'GitHub': 'https://github.com/ArtemLetyagin/Gesys'
  },
  include_package_data=True,
  python_requires='>=3.9'
)