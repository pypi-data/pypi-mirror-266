Third Party
====================================================================================================
This collection of files supports a minimal execute of Pyscript fully-self hosted and is based on their 2023.11.2 release. Note that this includes various sources from other open source projects:

 - es.js under the [ISC License (Andrea Giammarchi)](https://en.wikipedia.org/wiki/ISC_license).
 - [micropip](https://github.com/pyodide/micropip) under the [MPL 2.0 License](https://github.com/pyodide/micropip/blob/main/LICENSE).
 - [packaging](https://packaging.pypa.io/en/stable/) under the [BSD License](https://github.com/pypa/packaging/blob/main/LICENSE.BSD).
 - [Pyodide](https://github.com/pyodide/pyodide) under the [MPL 2.0 License](https://github.com/pyodide/pyodide/blob/main/LICENSE).
 - [Pyscript](https://pyscript.net/) under the [Apache v2 License](https://pyscript.github.io/docs/2023.12.1/license/).
 - [toml (Jak Wings)](https://www.npmjs.com/package/tomlify-j0.4?activeTab=readme) under the [MIT License](https://www.npmjs.com/package/tomlify-j0.4?activeTab=code)

Note that some of these pyscript sources have been slightly modified from upstream to support self-hosting whereas they typically expect to run under CDN. At time of writing, only a source change currently allows for this alternative behavior.