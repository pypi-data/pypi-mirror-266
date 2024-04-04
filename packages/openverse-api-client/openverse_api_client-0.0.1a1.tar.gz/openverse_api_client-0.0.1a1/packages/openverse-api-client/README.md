# @openverse/api-client

Thoroughly typed JavaScript client for the Openverse API.

[![Repository](https://img.shields.io/badge/sr.ht-~sara%2Fopenverse--api--client-%23c52b9b?logo=sourcehut)](https://sr.ht/~sara/openverse-api-client)
[![NPM Version](https://img.shields.io/npm/v/%40openverse%2Fapi-client)](https://www.npmjs.com/package/@openverse/api-client)

---

## Installation

```console
npm install @openverse/api-client
```

The [`cross-fetch`](https://github.com/lquixada/cross-fetch) dependency is
optional, and only needed when using the Openverse API client in a setting where
fetch is not globally available on `window` (e.g., server-side). If `fetch` is
globally available, the client will always use it. Otherwise, it will attempt to
use `cross-fetch`.

`@openverse/api-client` ships its own type definitions. `cross-fetch` was chosen
for Node and browser interoperability instead of directly using `node-fetch`,
because `cross-fetch` uses types identical in structure to browser `fetch`,
significantly simplifying request and response type management.

`cross-fetch` will not be used if `globalThis.fetch` is defined. That means
Node's native `fetch` will be used when available, and browser's native fetch is
always used. If you target environments that do not have `globalThis.fetch`
available, `cross-fetch` is used. To avoid `cross-fetch` for any reason,
polyfill `globalThis.fetch` to your preferred implementation.

## Usage

Requests to the Openverse API are made through a function returned by
`OpenverseClient`. The function accepts a string parameter representing the
endpoint's method and route. TypeScript infers the possible query parameters for
that endpoint, which are passed as the `params` property of the second argument.

```ts
import { OpenverseClient } from "@openverse/api-client";

const openverse = OpenverseClient();

const images = await openverse("GET v1/images/", {
    params: {
        q: "dogs",
        license: "by-nc-sa",
        source: ["flickr", "wikimedia"],
    },
});

images.body.results.forEach((image) => console.log(image.title));
```

All responses bear the following properties:

-   `body`: The API response. For JSON responses, this will be an object. For
    all others (e.g., thumbnail requests), this will be an untouched
    `ReadableStream` (`response.body` from `fetch`).
-   `meta`: An object containing the following information about the request:
    -   `headers`: Response headers
    -   `status`: The status of the response
    -   `url`: The final URL, including query parameters, the client made the
        request with
    -   `request`: The `RequestInit` object pased to fetch, including `headers`
        and `body`.

### Rate limiting

The requester function does _not_ automatically handle rate limit back-off. To
implement this yourself, check the rate limit headers from the response
`meta.headers`.

### Authentication

By default, the `OpenverseClient` function will return an unauthenticated
client.

To use an authenticated client, pass a `credentials` object containing
`clientId` and `clientSecret` to the `OpenverseClient` function. The client will
automatically request tokens as needed, including upon expiration.

```ts
import { OpenverseClient } from "@openverse/api-client";

const authenticatedOpenverse = OpenverseClient({
    credentials: {
        clientId: "...",
        clientSecret: "...",
    },
});
```

`OpenverseClient` automatically requests API tokens when authenticated,
including eagerly refreshing tokens to avoid halting ongoing requests. This is
safe, as the Openverse API does not immediately expire existing tokens when a
new one issued. This also means you do not need to share the same token between
multiple client instances (e.g., across multiple instances of the same
application, as in an application server cluster).

### Alternative Openverse API instances

By default, the main Openverse API is used at
https://api.openverse.engineering/. Other Openverse API instances may be used by
passing `baseUrl` to the `OpenverseClient` function:

```ts
import { OpenverseClient } from "@openverse/api-client";

const localhostOpenverse = OpenverseClient({
    baseUrl: "localhost:50280",
});
```

## License

`@openverse/api-client` is distributed under the terms of the
[GNU Lesser General Public License v3.0 or later](https://spdx.org/licenses/LGPL-3.0-or-later.html)
license.
