========================
Watcher Metering Drivers
========================

Introduction
============

Watcher Metering Drivers provides a set of metric-pulling drivers extending the
`Watcher Metering`_ project which is used to collect system metrics before publishing them to a given store.
To sum up, Watcher Metering service is composed by 2 modules:

- The ``Agent`` who collects the desired metrics and sends it to a publisher.
- The ``Publisher`` who gathers measurements from one or more agent and pushes
  them to the desired store. 

Drivers easily extend metrics collecting features of Agent (we use `stevedore`_ library for managing plugins).

This project is part of the Watcher_ project.

.. _Watcher Metering: https://github.com/b-com/watcher-metering
.. _Watcher: https://wiki.openstack.org/wiki/Watcher
.. _stevedore: http://git.openstack.org/cgit/openstack/stevedore

Getting started
===============

System requirements
-------------------

Watcher Metering packages must be installed before installing the drivers. Please follow the installation procedure of the `Watcher Metering`_ project first.

Installation
------------

To install this package, just use *pip*:

.. code-block:: shell

    # pip install python-watcher_metering_drivers


Activate a driver
-----------------

Within the your Watcher Metering Agent configuration file ``/etc/watcher-metering/watcher-metering-agent.conf``, add the name of the driver entry point, in the ``[agent]`` section,  you wish to enable.

As an example, if you wish to acticate both the ``cpu_user`` and the
``disk_free`` drivers, just edit the aforementioned configuration file like
this:

.. code-block:: ini

     [agent]
     driver_names =  
        cpu_user,
        disk_free
     
After updating the configuration file, you have to `restart the Watcher Metering Agent`_.

.. _restart the Watcher Metering Agent: https://github.com/b-com/watcher-metering/blob/master/doc/source/deploy/installation.rst#command

Driver configuration
====================

List of drivers implemented in this project are the following:
    - **cpu_count**: number of CPU cores available on host machine
    - **cpu_user**:percentage of CPU resources allocated to user processes on host machine
    - **cpu_idle**: percentage of CPU resources not used on host machine
    - **disk_total**: total disk size of host machine 
    - **disk_used**:  used disk size on host machine
    - **disk_free**:  free disk size of host machine
    - **memory_total**: total memory size on host machine 
    - **memory_used**: used memory size on host machine
    - **memory_free**: free memory size on host machine
    - **instance_cpu_used**: percentage of CPU resources used on an instance running on the host machine
    - **swap_total**: total memory swap size on host machine
    - **swap_used**: used memory swap size on host machine
    - **swap_free**: free memory swap size on host machine

Each driver can be also configurable by adding a dedicated section named ``[[metrics_driver.driver_name]`` in a configuration file loaded by the Watcher Metering Agent. Such a file is self documented, so you will find in it all driver configuration documentation. 

You will find a sample by editing the file `etc/watcher-metering-drivers/watcher-metering-drivers.conf.sample`_

.. _etc/watcher-metering-drivers/watcher-metering-drivers.conf.sample: etc/watcher-metering-drivers/watcher-metering-drivers.conf.sample.

