# RHDZMOTA EXT: hello_world

Package extensions have 2 main purposes:
* Split the dependency sets into several smaller python projects
* Serve as domain-specific packages (i.e., split functionality).

## About the `hello_world` extension

This package extension is intended to be used as reference and for testing purposes. It contains a simple
(almost trivial) implementation of the classic hello-world example.

## Linked Installation

Most extensions can be installed indirectly via the main package by providing an extra-dependency tag. Example:

```commandline
$ pip install 'rhdzmota[ext.hello_world]'
```
* General pattern: `'rhdzmota[ext.{{extension-slug}}]'`

## Standalone Installations

Package extensions can also be installed independently. For example:

```commandline
$ pip install rhdzmota_extension_hello_world
```
* General pattern: `rhdzmota_extension_{{extension-slug}}`

You can also install them locally:

```commandline
$ EXT_BUILD_LOCAL=1 pip install -e extensions/hello_world
```
* General pattern: `EXT_BUILD_LOCAL=1 pip install -e path/to/extension`

