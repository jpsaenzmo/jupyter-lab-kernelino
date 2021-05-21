arduino_kernel
===========

``arduino_kernel`` is a simple example of a Jupyter kernel. This repository
complements the documentation on wrapper kernels here:

http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html

Installation
------------
To install ``arduino_kernel`` from PyPI::

    pip install ./kernel
    python -m arduino_kernel.install

Using the Arduino kernel
---------------------
**Notebook**: The *New* menu in the notebook should show an option for an Arduino notebook.

**Console frontends**: To use it with the console frontends, add ``--kernel echo`` to
their command line arguments.
