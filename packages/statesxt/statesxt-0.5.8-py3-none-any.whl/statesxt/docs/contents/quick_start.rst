###########
Quick Start
###########

This section covers steps for installation and a guide on how to use.

How to Install?
===============
There are two approaches to install the package:

* Manually cloning the project in Github repository: `statesxt <https://github.com/cjsonnnnn/statesxt>`_
* Using ``pip``, that the package is hosted in `here <https://test.pypi.org/project/statesxt/>`_ **(recommended)**. Currently, due to the Pypi repository being down and is blocking any account registers and project uploads, the package is now hosted on TestPypi for the time being.
  
  .. code-block:: bash

    pip install -i https://test.pypi.org/simple/ statesxt

.. tip:: 
  It is always better to install the package in a virtual environment.


How to Use?
===========

* Generate the template

  .. code-block:: bash
    
    statesxt gen

* Remove the template

  .. code-block:: bash
    
    statesxt rem


How to Update?
==============
Currently, the package can not be updated through usual command ``pip install --upgrade statesxt``. Probably because is hosted in TestPypi. So, for the time being, user have to reinstall the package.


How to Uninstall?
=================
There are two approaches to uninstall the package:

* Uninstalling only the package

  .. code-block:: bash
    
    pip uninstall statesxt

* Uninstalling the package and its dependencies **(vulnerable)**. To do this, the user must install a package called ``pip-autoremove`` (if not already installed).

  .. code-block:: bash
    
    pip install pip-autoremove

  Once the package is installed, user can now uninstall the package with the following command.

  .. code-block:: bash
    
    pip-autoremove statesxt -y

  .. note::
    If there is an error saying that ``ModuleNotFoundError: No module named 'pip_autoremove'``, you could try to move the ``pip_autoremove.py`` file from ``./Scripts`` into ``./Lib`` instead. 
    
    For further information:
    https://stackoverflow.com/questions/74523001/modulenotfounderror-when-trying-to-use-pip-autoremove






