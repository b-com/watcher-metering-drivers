============================================================
Welcome to Watcher Metering Drivers' developer documentation
============================================================

Introduction
============

Watcher Metering Drivers provides a set of metric-pulling drivers extending the
python-watcher_metering_ package.

Watcher Metering collects system metrics and publishes them to a store.
To do so, it is composed of two elements:

- The ``Agent`` who collects the desired metrics and sends it to a publisher.
  The ``Agent`` is meant to run on each monitored host (container, VM, ...)
- The ``Publisher`` who gathers measurements from one or more agent and pushes
  them to the desired store. The currently supported stores are Riemann
  (for CEP) and Ceilometer.

This package is part of the Watcher_ project.

For more information on Watcher_, you can also refer to its OpenStack wiki_
page.

.. _python-watcher_metering: https://pypi.python.org/pypi/python-watcher_metering
.. _Watcher: http://factory.b-com.com/www/watcher/watcher/doc/build/html/
.. _wiki: https://wiki.openstack.org/wiki/Watcher


Developer Guide
===============

API References
--------------

.. toctree::
    :maxdepth: 2

    api/reference


Admin Guide
===========

Installation
------------

.. toctree::
  :maxdepth: 1

  deploy/installation


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
