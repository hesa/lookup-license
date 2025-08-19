<!--
SPDX-FileCopyrightText: 2025 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Purl

You can use lookup-license to identify the license, using the Naive license identify as described below, for a purl package. 

## Gem

Look up license for gem package `pkg:gem/google-apis-core@0.11.1`:

```
$ lookup-license --purl pkg:gem/google-apis-core@0.11.1
Apache-2.0
```

Look up license for gem package `pkg:gem/google-apis-core@0.11.1` with verbose output:

```
$ lookup-license --purl pkg:gem/google-apis-core@0.11.1 -v
Name:                google-apis-core
Version:             0.11.1
Homepage:            https://github.com/google/google-api-ruby-client
Repository:          https://github.com/googleapis/google-api-ruby-client/tree/0.11.1
Original url:        pkg:gem/google-apis-core@0.11.1
License identified:  Apache-2.0
License identified in repository:
 * Apache-2.0 <-- https://raw.githubusercontent.com/googleapis/google-api-ruby-client/refs/tags/0.11.1/LICENSE
 * Apache-2.0 <-- https://raw.githubusercontent.com/googleapis/google-api-ruby-client/refs/tags/0.11.1/README.md
License identified in package configuration:
 * Apache-2.0 <-- https://rubygems.org/api/v2/rubygems/google-apis-core/versions/0.11.1.json
```

## Github

Look up license for gem package `pkg:github/bcomnes/netrc-creds@v2.1.4` with verbose output:

```
$ ./devel/lookup-license --purl pkg:github/bcomnes/netrc-creds@v2.1.4 
MIT
```


## Go

Currently not supported.

## Maven

Currently not supported.

## Pypi

Look up license for gem package `pkg:pypi/boto3@1.35.99`:

```
$ ./devel/lookup-license --purl pkg:pypi/boto3@1.35.99
Apache-2.0 AND License :: OSI Approved :: Apache Software License
```

## Swift

Look up license for gem package `pkg:swift/github.com/google/abseil-cpp-binary@1.2024011602.0`:

```
$ ./devel/lookup-license --purl pkg:swift/github.com/google/abseil-cpp-binary@1.2024011602.0
WARNING:root:Could not identify a repository for pkg:swift/github.com/google/abseil-cpp-binary@1.2024011602.0
WARNING:root:Could not identify one single repository for pkg:swift/github.com/google/abseil-cpp-binary@1.2024011602.0. Found 0 urls: []
Apache-2.0
```

# Gem package

Look up license for gem package `google-apis-core@0.11.1`:

```
$ lookup-license --gem google-apis-core@0.11.1
Apache-2.0
```

Look up license for gem package `google-apis-core@0.11.1` with verbose output:

```
$ lookup-license --gem google-apis-core@0.11.1 -v
Name:                google-apis-core
Version:             0.11.1
Homepage:            https://github.com/google/google-api-ruby-client
Repository:          https://github.com/googleapis/google-api-ruby-client/tree/0.11.1
Original url:        google-apis-core@0.11.1
License identified:  Apache-2.0
License identified in repository:
 * Apache-2.0 <-- https://raw.githubusercontent.com/googleapis/google-api-ruby-client/refs/tags/0.11.1/LICENSE
 * Apache-2.0 <-- https://raw.githubusercontent.com/googleapis/google-api-ruby-client/refs/tags/0.11.1/README.md
License identified in package configuration:
 * Apache-2.0 <-- https://rubygems.org/api/v2/rubygems/google-apis-core/versions/0.11.1.json
```

# Pypi package

Look up license for pypi package `boto3@1.35.99`:

```
$ ./devel/lookup-license --pypi boto3@1.35.99
Apache-2.0 AND License :: OSI Approved :: Apache Software License
```


# Git repository

# Swift package


Look up license for swift package `leveldb@1.22.5`:

```
$ ./devel/lookup-license --swift leveldb@1.22.5
BSD-3-Clause AND generic-cla
```

# Naive license identification

## Source code repository

* If no verion or branch is provided, well known branch names are checked one by one and once one is found it is used.

* Well known license files (e.g. LICENSE, COPYING) are searched for licenses.

* The licenses identified above are presented

Note: reuse folder `LICENSES` is not checked for licenses

Note: Currently only git repositories are supported.

## Package

## Purl

If the purl is a github purl, then the license is looked up as a source code repository.

If the purl is a software package (e.g. a Pypi package), then the license is looked up:

* find the metadata for the package and in that:

    * use the license 

    * find the source code repository and look up the license as a source code repository

* present all the licenses identifed 
