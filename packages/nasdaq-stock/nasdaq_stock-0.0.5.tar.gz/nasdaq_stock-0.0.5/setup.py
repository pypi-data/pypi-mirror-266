from distutils.core import setup

setup(
  name = 'nasdaq_stock',
  packages = ['nasdaq_stock'],
  version = '0.0.5',
  description = 'nasdaq stock retriever',
  long_description = open('README.md').read(),
  author = 'George Shen',
  author_email = 'georgejs.arch@gmail.com',
  url = 'https://github.com/georgejs/nasdaq_stock',
  download_url = 'https://github.com/georgejs/nasdaq_stock/archive/0.0.5.tar.gz',
  install_requires=['lxml'],
  keywords = ['stock', 'nasdaq', 'stock retriever', 'nasdaq stock'],
  classifiers = [],
)
