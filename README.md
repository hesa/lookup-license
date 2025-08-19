<!--
SPDX-FileCopyrightText: 2024 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Lookup License

Python tool to identify license from license text or license names.

With `lookup-license` you can lookup licenses from:

* text (e.g. an incorrect name such as "BSD3" or an entire license text)

* file (e.g. "src/LICENSE.txt")

* url (e.g. "https://github.com/hesa/lookup-license/blob/main/LICENSE")

* repositories

* package names

* purls

The first lookup takes a bit of time, due to initialization, so if you
want to do a number of lookups you might want to use the interactive
shell.

# Using `lookup-license`

## Lookup license without argument

If you do not provide an argument `lookup-license` assumes you want to copy/paste license information interactively. Let's say we want to lookup the license `mit`.

```
$ lookup-license
Enter license text and press Control-d.
>>> mit
MIT
```

In the example above:

* `Enter license text and press Control-d.` is usage information

* `>>>` is the `lookup-license` prompt

* `mit` is the input the user provided

* `MIT` is the result from `lookup-license`


## Lookup license passed as an argument

You want to lookup the license "MIT AND BSD3":
```
$ lookup-license "MIT AND BSD3"
MIT AND BSD-3-Clause
```
## Lookup license information in a file

If you pass a file name without the `--file` option the file name is treated as an argument containing license text. So the following will *not* lookup the license text in `LICENSE.TXT`.
```
$ lookup-license "LICENSE.TXT"
```

If you want `lookup-license` to read the content and try to identify the license based on that, then you need to use the `--file` option.

### Interactively provide the file name

```
$ lookup-license --file
Enter license file name and press enter.
>>> LICENSE.txt
CC-BY-4.0
```

### Provide the file name as an argument

```
$ lookup-license --file LICENSE.txt
CC-BY-4.0
```

# Lookup license information form a URL

Same as described earlier with file names, if you pass a URL to `lookup-license` it will be treated as license information. If you want to lookup the URL content you need to use the `--url` option.

### Interactively provide the URL

```
$ lookup-license --url
Enter license URL name and press enter.
>>> https://github.com/psf/requests/blob/main/LICENSE
Apache-2.0
```

### Provide the URL as an argument

```
$ lookup-license --url https://github.com/psf/requests/blob/main/LICENSE
Apache-2.0
```

## interactive shell

Here is an example session for looking up the text `mit` followed the URL `https://github.com/psf/requests/blob/main/LICENSE`:

```
$ lookup-license --shell
Welcome to the LookupLicense shell. Type help or ? to list commands.

>>> text 
Enter license text and press Control-d.
>>> mit
['MIT']
>>> url 
Enter license URL name and press enter.
>>> https://github.com/psf/requests/blob/main/LICENSE
['Apache-2.0']
```

## Looking up locense for packages and repositories

With `lookup-license` you can lookup the license for packages and repositories using:

* Purls (Gem, github, Pypi, Swift)

* Gitrepo (github, gitlab, freedesktop)

* Package names (Gem, github, Pypi, Swift)

See [Purl and package managers](PURL_AND_MISC.md) for more information.

# Acknowledgements

Lookup license is a tiny wrapper on top of the following python modules:

* [scancode](https://github.com/nexB/scancode-toolkit) and [ScanCode LicenseDB](https://scancode-licensedb.aboutcode.org/) used to when looking up license text. Big thanks to [Nexb](https://www.nexb.com/).

* [foss-licenses](https://github.com/hesa/foss-licenses), used when looking up license identifiers.


