# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['pypcl']

package_data = \
{'': ['*']}

install_requires = \
['cmake>=3.29.0.1,<4.0.0.0',
 'cython>=3.0.9,<4.0.0',
 'ninja>=1.11.1.1,<2.0.0.0',
 'numpy>=1.26.4,<2.0.0',
 'scikit-build>=0.17.6,<0.18.0',
 'setuptools>=69.2.0,<70.0.0',
 'tqdm>=4.66.2,<5.0.0']

setup_kwargs = {
    'name': 'pcl-python',
    'version': '0.0.3',
    'description': 'Point Cloud Library for Python',
    'long_description': '# Point Cloud Library for Python\n\n## How to install\n\n```bash\npip install git+https://github.com/turingmotors/PyPcl.git\n```\n\n## How to build [WIP]\n\n依存パッケージをインストール\n\n```bash\nsudo apt install libpcl-dev\n```\n\nwheel ファイルの作成\n\n```bash\ngit clone https://github.com/turingmotors/PyPcl.git\ncd PyPcl\npoetry install\npoetry run python setup.py bdist_wheel\n```\n\n`/dist` 下の whl ファイルを pip でインストールできる。\n',
    'author': 'emanuere',
    'author_email': 'smtn10hryk28@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
