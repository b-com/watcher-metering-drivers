=========================
Deployment - installation
=========================

Watcher Metering Drivers
========================

Installation
------------

System requirements
-------------------

As this package extends python-watcher_metering_, please make sure you
installed its system dependencies before continuing.

.. _python-watcher_metering: https://pypi.python.org/pypi/python-watcher_metering


Installation
------------

To install this package, just use *pip*:

.. code-block:: shell

    $ pip install python-watcher_metering_drivers


Activate a driver
-----------------

Within the your watcher metering configuration file, add the name of the driver
entry point you wish to enable.

As an example, if you wish to acticate both the ``cpu_user`` and the
``disk_free`` drivers, just edit the aforementioned configuration file like
this:

.. code-block:: ini

     [agent]
     driver_names =  cpu_user,disk_free
     # ...


Running the application
-----------------------

To run our Watcher Metering agent, you can use the following command


Driver configuration
====================

To configure a driver, you can specify it in a separate configuration file.
Please refer to the comments left within the ``$(ROOT_DIR)/etc/watcher-metering``\
``/watcher-metering-drivers.conf`` sample to get more details on the
configuration options.

Then, to run the agent using our driver configuration, you can use the
following command:

.. code-block:: shell

    $ watcher-metering-agent \
        --config-file=$(WATCHER_METERING_AGENT_CONFIG_FILE)
        --config-file=$(WATCHER_METERING_DRIVERS_CONFIG_FILE)
