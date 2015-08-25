.. include globals.rst

Vizydrop `concurrent_external_api` Example
==========================================

The concurrent_external_api example reads data from multiple API's using toro queues and concurrent HTTP calls.
This helps speed up the gathering of external data split across multiple API's, endpoints, or searches and can
tremendously lower request times.  This example includes no authentication, does not provide a source schema, and is
not actually connected to an external API.  It is merely provided as an advanced example of how to implement concurrent
HTTP calls.  This example requires the `toro` package available on PyPi.