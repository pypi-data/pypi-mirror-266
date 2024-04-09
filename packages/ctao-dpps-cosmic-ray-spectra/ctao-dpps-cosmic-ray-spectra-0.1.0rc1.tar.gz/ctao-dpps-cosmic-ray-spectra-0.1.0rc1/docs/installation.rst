Installation
============

User Installation
-----------------

This project has not yet published packages, for now, follow the developer instructions.


Developer Setup
---------------

As a developer, clone the repository, create a virtual environment
and then install the package in development mode:

.. code-block:: shell

   $ git clone git@gitlab.cta-observatory.org:cta-computing/dpps/cosmic-ray-spectra
   $ cd cosmic-ray-spectra
   $ python -m venv venv
   $ source venv/bin/activate
   $ pip install -e ".[all]"

The same also works with conda, create a conda env instead of a venv above.
