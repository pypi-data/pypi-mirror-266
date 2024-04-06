# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['specsanalyzer', 'specsscan']

package_data = \
{'': ['*'], 'specsanalyzer': ['config/*'], 'specsscan': ['config/*']}

install_requires = \
['h5py>=3.6.0',
 'imutils>=0.5.4',
 'ipympl>=0.9.1',
 'ipywidgets>=7.7.1',
 'matplotlib>=3.5.1',
 'numpy>=1.21.6',
 'opencv-python>=4.8.1.78',
 'pynxtools-mpes>=0.0.1',
 'python-dateutil>=2.8.2',
 'pyyaml>=6.0',
 'scipy>=1.8.0',
 'tifffile>=2022.5.4',
 'xarray>=0.20.2']

extras_require = \
{'notebook': ['jupyter[notebook]>=1.0.0',
              'ipykernel[notebook]>=6.9.1',
              'jupyterlab-h5web[notebook]>=7.0.0']}

setup_kwargs = {
    'name': 'specsanalyzer',
    'version': '0.1.6a0',
    'description': 'Python package for loading and converting SPECS Phoibos analyzer data.',
    'long_description': '[![Documentation Status](https://github.com/OpenCOMPES/specsanalyzer/actions/workflows/documentation.yml/badge.svg)](https://opencompes.github.io/specsanalyzer/)\n[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)\n![](https://github.com/OpenCOMPES/specsanalyzer/actions/workflows/linting.yml/badge.svg)\n![](https://github.com/OpenCOMPES/specsanalyzer/actions/workflows/testing_multiversion.yml/badge.svg?branch=main)\n![](https://img.shields.io/pypi/pyversions/specsanalyzer)\n![](https://img.shields.io/pypi/l/specsanalyzer)\n[![](https://img.shields.io/pypi/v/specsanalyzer)](https://pypi.org/project/specsanalyzer)\n[![Coverage Status](https://coveralls.io/repos/github/OpenCOMPES/specsanalyzer/badge.svg?branch=main&kill_cache=1)](https://coveralls.io/github/OpenCOMPES/specsanalyzer?branch=main)\n\n# specsanalyzer\nThis is the package `specsanalyzer` for conversion and handling of SPECS Phoibos analyzer data.\n\nThis package contains two modules:\n`specsanalyzer` is a package to import and convert MCP analyzer images from SPECS Phoibos analyzers into energy and emission angle/physical coordinates.\n`specsscan` is a Python package for loading Specs Phoibos scans accquired with the labview software developed at FHI/EPFL\n\nTutorials for usage and the API documentation can be found in the [Documentation](https://opencompes.github.io/specsanalyzer/)\n\n## Installation\n\n### Pip (for users)\n\n- Create a new virtual environment using either venv, pyenv, conda, etc. See below for an example.\n\n```bash\npython -m venv .specs-venv\n```\n\n- Activate your environment:\n\n```bash\nsource .specs-venv/bin/activate\n```\n\n- Install `specsanalyzer` from PyPI:\n\n```bash\npip install specsanalyzer\n```\n\n- This should install all the requirements to run `specsanalyzer` and `specsscan`in your environment.\n\n- If you intend to work with Jupyter notebooks, it is helpful to install a Jupyter kernel for your environment. This can be done, once your environment is activated, by typing:\n\n```bash\npython -m ipykernel install --user --name=specs_kernel\n```\n\n#### Configuration and calib2d file\nThe conversion procedures require to set up several configuration parameters in a config file. An example config file is provided as part of the package (see documentation). Configuration files can either be passed to the class constructures, or are read from system-wide or user-defined locations (see documentation).\n\nMost importantly, conversion of analyzer data to energy/angular coordinates requires detector calibration data provided by the manufacturer. The corresponding *.calib2d file (e.g. phoibos150.calbid2d) are provided together with the spectrometer software, and need to be set in the config file.\n\n### For Contributors\n\nTo contribute to the development of `specsanalyzer`, you can follow these steps:\n\n1. Clone the repository:\n\n```bash\ngit clone https://github.com/OpenCOMPES/specsanalyzer.git\ncd specsanalyzer\n```\n\n2. Check out test data (optional, requires access rights):\n\n```bash\ngit submodule sync --recursive\ngit submodule update --init --recursive\n```\n\n2. Install the repository in editable mode:\n\n```bash\npip install -e .\n```\n\nNow you have the development version of `specsanalyzer` installed in your local environment. Feel free to make changes and submit pull requests.\n\n### Poetry (for maintainers)\n\n- Prerequisites:\n  + Poetry: https://python-poetry.org/docs/\n\n- Create a virtual environment by typing:\n\n```bash\npoetry shell\n```\n\n- A new shell will be spawned with the new environment activated.\n\n- Install the dependencies from the `pyproject.toml` by typing:\n\n```bash\npoetry install --with dev, docs\n```\n\n- If you wish to use the virtual environment created by Poetry to work in a Jupyter notebook, you first need to install the optional notebook dependencies and then create a Jupyter kernel for that.\n\n  + Install the optional dependencies `ipykernel` and `jupyter`:\n\n  ```bash\n  poetry install -E notebook\n  ```\n\n  + Make sure to run the command below within your virtual environment (`poetry run` ensures this) by typing:\n\n  ```bash\n  poetry run ipython kernel install --user --name=specs_poetry\n  ```\n\n  + The new kernel will now be available in your Jupyter kernels list.\n',
    'author': 'Laurenz Rettig',
    'author_email': 'rettig@fhi-berlin.mpg.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mpes-kit/specsanalyzer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
