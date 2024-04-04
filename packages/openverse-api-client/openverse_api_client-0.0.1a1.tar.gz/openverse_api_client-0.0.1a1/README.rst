openverse-api-client
====================

A thoroughly typed Python client for the Openverse API.

|Repository| |PyPI - Version| |PyPI - Python Version|

Installation
------------

.. code:: bash

    pip install openverse-api-client


Usage
-----

The Openverse API client has a single external dependency on ``httpx``. `HTTPx`_ was chosen because the precense of both a synchronous and asynchronous HTTP client from a single library, with nearly identical APIs, made it easy to generate the Python client using the generator.

.. code:: python

    from openverse_api_client import OpenverseClient, AsyncOpenverseClient

    with OpenverseClient() as openverse:
        images = openverse.GET_v1_images(
            q="dogs",
            license="by-nc-sa",
            source=["flickr", "wikimedia"],
        )

    with AsyncOpenverseClient() as async_openverse:
        audio = await async_openverse.GET_v1_audio(
            q="birds",
            license="by",
            source=["freesound"],
        )


Using the Openverse client as context managers will automatically close the underlying HTTPx client. Call ``close`` on the Openverse client to manually close the underlying HTTPx client when not using the context manager.

Shared HTTPx client session
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you already use HTTPx and utilised a shared client session, you may pass this to the Openverse client constructors.

.. code:: python

    from openverse_api_client import OpenverseClient
    import httpx

    httpx_client = httpx.Client()

    openverse = OpenverseClient(
        httpx_client=httpx_client,
    )

The same API applies for the asynchronous Openverse client, but requires ``httpx.AsyncClient`` instead.

When using a shared HTTPx client session **do not call close on the Openverse client** as this will close the shared HTTPx instance. Likewise, **do not use the Openverse client context manager if passing in a shared client**, the context manager will close your shared HTTPx client on context exit.

Authentication
^^^^^^^^^^^^^^

By default, the clients will make unauthenticated requests. Pass ``client_id`` and ``client_secret`` to the client constructor to authenticate requests. The client automatically handles requesting tokens and token expiration.

.. code:: python

    from openverse_api_client import OpenverseClient

    # The same API applies to the async client
    authenticated_openverse = OpenverseClient(
        client_id="...",
        client_secret="...",
    )

Alternative Openverse API instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The clients reference the official production Openverse API instance by default, https://api.openverse.engineering. If you would like to send requests to a different API instance, pass ``base_url`` to the constructor:

.. code:: python

    from openverse_api_client import OpenverseClient

    # The same API applies to the async client
    localhost_openverse = OpenverseClient(
        base_url="localhost:50280",
    )

Development
-----------

Please refer to the repository README

License
-------

`openverse-api-client` is distributed under the terms of the `GNU Lesser General Public License v3.0 or later`_ license.

.. _GNU Lesser General Public License v3.0 or later: https://spdx.org/licenses/LGPL-3.0-or-later.html
.. _HTTPx: https://www.python-httpx.org/

.. |Repository| image:: https://img.shields.io/badge/sr.ht-~sara%2Fopenverse--api--client-%23c52b9b?logo=sourcehut
   :target: https://sr.ht/~sara/openverse-api-client

.. |PyPI - Version| image:: https://img.shields.io/pypi/v/openverse-api-client.svg
    :target: https://pypi.org/project/openverse-api-client

.. |PyPI - Python Version| image:: https://img.shields.io/pypi/pyversions/openverse-api-client.svg
    :target: https://pypi.org/project/openverse-api-client
