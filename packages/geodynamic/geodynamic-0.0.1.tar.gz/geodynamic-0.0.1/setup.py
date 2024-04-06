from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='geodynamic',
  version='0.0.1',
  author='ivaleo',
  author_email='ivaleotion@gmail.com',
  description='Geometric tools for parsing GeoGebra construction, proccess with manim animation and export to SVG',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://gitlab.mathem.ru/',
  packages=find_packages(),
  install_requires=[
      'requests>=2.25.1',
      'numpy>=1.26.0',
      'manim>=0.18.0',
      'manim-mobject-svg>=0.5.0',
      ],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='geometry dynamic geogebra manim animation svg python',
  #project_urls={
  #  'Documentation': 'https://gitlab.mathem.ru/'
  #},
  python_requires='>=3.7'
)

print(find_packages())
