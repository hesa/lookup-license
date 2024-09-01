<!--
SPDX-FileCopyrightText: 2024 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Lookup License

Python tool to identify license from license text or license names.

With `lookup-license` you can lookup the license from:

* text (e.g. an incorrect name such as "BSD3" or an entire license text)

* file (e.g. "src/LICENSE.txt")

* url (e.g. "https://github.com/hesa/lookup-license/blob/main/LICENSE")

The first lookup takes a bit of time, due to initialization, so if you
want to do a number of lookups you might want to use the interactive
shell.

# Using `lookup+license`

##  Text lookup

You want to lookup the license "MIT AND BSD3":
```
$ lookup-license "MIT AND BSD3"
```


lookup-license MIT AND BSD3

;; lookup-license filename ; this will not work since the license text
  may actually be sth along the lines "LICENSE.txt"

lookup-license 
> Enter license text and press Control-d.

# File lookup
lookup-license --file filename

lookup-license --file 
> Enter license file name and press Control-d.

# Url lookup
lookup-license --url URL

lookup-license --url 
> URL

# shell
lookup-license --shell

lookup-license shell>
Welcome to the LookupLicense shell. Type help or ? to list commands.

LookupLicense> text


lookup-license shell> text
> Enter license text and press Control-d.

lookup-license shell> file
> Enter license file name and press Control-d.

# Acknowledgements

Lookup license is a tiny wrapper on top of the following tools:

* [scancode](https://github.com/nexB/scancode-toolkit) and [ScanCode LicenseDB](https://scancode-licensedb.aboutcode.org/). Thanks to [Nexb](https://www.nexb.com/).

* [foss-licenses](https://github.com/hesa/foss-licenses).
