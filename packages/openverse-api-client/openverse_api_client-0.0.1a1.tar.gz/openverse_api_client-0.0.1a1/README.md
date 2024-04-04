# openverse-api-client

Fully typed Openverse API clients for Python and JavaScript.

[![Repository](https://img.shields.io/badge/sr.ht-~sara%2Fopenverse--api--client-%23c52b9b?logo=sourcehut)](https://sr.ht/~sara/openverse-api-client)
[![PyPI - Version](https://img.shields.io/pypi/v/openverse-api-client.svg)](https://pypi.org/project/openverse-api-client)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openverse-api-client.svg)](https://pypi.org/project/openverse-api-client)
[![NPM Version](https://img.shields.io/npm/v/%40openverse%2Fapi-client)](https://www.npmjs.com/package/@openverse/api-client)

---

## Client libraries

-   Python: https://pypi.org/project/openverse-api-client
-   JavaScript: https://www.npmjs.com/package/@openverse/api-client

## Development

**Dependencies**:

-   `hatch`
-   `pnpm`
-   `just`

This project generates Python and TypeScript clients for the Openverse API,
based on endpoint definitions written in Python, and Jinja2 templates for Python
and TypeScript files. A full build of both clients requires the following steps:

1. Generating the client code: `hatch run generate`
2. Building the npm package (including TypeScript definitions):
   `just pnpm build`
    - Run `just pnpm install` if this is the first run
3. Building the Python package: `hatch build`

The `just build` recipe encapsulates these tasks into a single command. Each
task can run on its own for debugging different parts of the client code
generation or build process.

In most cases, you will need to run at least `hatch run generate` for
development tools to work, because otherwise critical files will be missing that
other runtime code depends on.

The Python clients live in the same package as the client generation code, which
allows them to reuse the endpoint definitions for Python type hints without
introducing an intermediary package. The Jinja2 dependency is optional, and only
installed when the `generator` feature is installed (i.e.,
`pip install openverse-api-client[generator]`).

The CLI (`generate-openverse-api-client` or `hatch run generate`) accepts
arguments to control which languages are generated. Run `hatch run generate -h`
to view the CLI documentation.

Tests for both the Python and JavaScript clients should be run using `just`
recipes, which manage cleaning and regeneration of the clients on each run. For
Python:

```shell
just pytest
```

For JavaScript/TypeScript:

```shell
just tstest
```

### Contributing

Contributions are welcome using patchsets. You can submit these either via
Sourcehut's UI, or `git send-email`. Please refer to Sourcehut's documentation
and tutorial for this process:
https://man.sr.ht/git.sr.ht/#sending-patches-upstream.

Please send patches to
[`~sara/openverse-api-client-devel@lists.sr.ht`](mailto:~sara/openverse-api-client-devel@lists.sr.ht).

## License

`openverse-api-client` is distributed under the terms of the
[GNU Lesser General Public License v3.0 or later](https://spdx.org/licenses/LGPL-3.0-or-later.html)
license.
