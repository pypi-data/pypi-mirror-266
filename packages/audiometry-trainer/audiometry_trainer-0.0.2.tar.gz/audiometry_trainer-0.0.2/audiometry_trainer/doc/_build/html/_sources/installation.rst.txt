.. _sec-installation:

************
Installation
************

``audiometry_trainer`` has been successfully installed and used on Linux and Windows. It should also work on Mac platforms, but this has not been tested. A dedicated installer is provided for Windows. On Linux and Mac (and Windows if you do not wish to use the dedicated installer) ``audiometry_trainer``, which is written in Python, can be installed via the Python package installer ``pip``:

.. code-block:: bash

		pip install audiometry_trainer

``audiometry_trainer`` depends on a few Python modules including:

  * PyQt5
  * numpy
  * scipy
  * matplotlib
  * pandas

depending on your Python distribution you may want to install these dependecies before installing ``audiometry_trainer`` via ``pip`` (e.g. through ``conda`` if you're using the Anaconda Python distribution, or through your Linux distribution package manager if you're using the Python installation that comes with your Linux distribution), otherwise ``pip`` will attempt to automatically pull in and install these dependencies. If the program is successfully installed you should be able to start it from a bash/DOS terminal with the command:

.. code-block:: bash

	audiometry_trainer

You need to ensure that the Python environment you're using when you call the above command matches the one you used when you installed the application.






