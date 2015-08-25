.. include globals.rst

Vizydrop SDK Python Examples
============================

To help you get started with integrating your systems, platforms, and applications with Vizydrop, the Python SDK
package provides a few examples of varying use cases.  You can use these examples as a template to start developing
your own integrations.

The SDK supports only Python 3.3 and greater.


Examples
========

flatfile
--------

The flatfile example reads data from simple flat-files from the `data` directory and serves their information to
Vizydrop.  This example includes no authentication and does not provide a source schema.


external_api
------------

The external_api example reads data from an external RESTful API and serves its information to Vizydrop.  This example
does not include any authentication but does provide a source schema formatted according to its API.  This example draws
upon the `Consumer Complaint Database<http://catalog.data.gov/dataset/consumer-complaint-database>` from the US Consumer
Financial Protection Bureau.


concurrent_external_api
-----------------------

The concurrent_external_api example reads data from multiple API's using toro queues and concurrent HTTP calls.
This helps speed up the gathering of external data split across multiple API's, endpoints, or searches and can
tremendously lower request times.  This example includes no authentication, does not provide a source schema, and is
not actually connected to an external API.  It is merely provided as an advanced example of how to implement concurrent
HTTP calls.  This example requires the `toro` package available on PyPi.