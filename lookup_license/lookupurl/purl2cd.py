# SPDX-FileCopyrightText: 2025 DB Systel GmbH
#
# SPDX-License-Identifier: Apache-2.0

#
# This file contains source code from
# * https://github.com/OpenRailAssociation/purl-tools/blob/main/purltools/_git.py
# * https://github.com/OpenRailAssociation/purl-tools/blob/main/purltools/purl2cd.py
#

"""purl2clearlydefined and connected functions"""

import logging
import os # missing in original
import sys

from packageurl import PackageURL  # noqa: I900

import requests

def is_sha1(sha: str) -> bool:
    """Check if a string is a valid SHA1 hash.

    Args:
        sha (str): The string to check.

    Returns:
        bool: True if the string is a valid SHA1 hash, False otherwise.
    """
    return len(sha) == 40 and all(c in "0123456789abcdef" for c in sha.lower())


def github_tag_to_commit(owner: str, repo: str, tag: str) -> str:
    """Convert a GitHub tag to a commit hash.

    Args:
        tag (str): The GitHub tag.

    Returns:
        str: The commit hash corresponding to the tag.
    """
    return get_tag_commit_sha(owner, repo, tag)


def validate_tag_url(url: str) -> None:
    """Validate a GitHub API URL to prevent server-side request forgery"""
    if not url.startswith("https://api.github.com"):
        raise ValueError(f"Invalid GitHub API URL '{url}")
    if not is_sha1(url.split("/")[-1]):
        raise ValueError(f"Invalid SHA1 hash in URL '{url}'")


def get_github_token() -> str | None:
    """Get GitHub token from environment variable if available"""
    if "GITHUB_TOKEN" in os.environ and os.environ["GITHUB_TOKEN"]:
        logging.debug("GitHub token found in environment")
        return str(os.environ["GITHUB_TOKEN"])
    logging.debug("No GitHub token found, proceeding unauthenticated")
    return None


def get_tag_commit_sha(owner: str, repo: str, tag: str) -> str:
    """Convert a GitHub tag to a commit hash using GitHub's REST API.

    Args:
        owner (str): Repository owner
        repo (str): Repository name
        tag (str): Tag name/reference

    Returns:
        str: The commit SHA the tag points to

    Raises:
        requests.exceptions.RequestException: If the API request fails
    """
    token = get_github_token()
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/tags/{tag}"
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    # Tag refs point to annotated tags first, which then point to commits
    if data["object"]["type"] == "tag":
        # Get the commit URL from the annotated tag
        tag_url = data["object"]["url"]
        validate_tag_url(tag_url)
        tag_response = requests.get(tag_url, headers=headers, timeout=10)
        tag_response.raise_for_status()
        return tag_response.json()["object"]["sha"]

    # Lightweight tags point directly to commits
    return data["object"]["sha"]


def purl2clearlydefined(purl: str) -> str | None:
    """
    Converts a Package URL (purl) to ClearlyDefined coordinates.

    Parses the purl and translates it into a coordinate format compatible with
    ClearlyDefined, handling necessary type conversions and provider mappings.

    Args:
        purl (str): The Package URL to be converted.

    Returns:
        str: The ClearlyDefined coordinates derived from the purl.

    Raises:
        ValueError: If the provided purl is not valid, cannot be parsed by the
        PackageURL module, or if the package type is not supported.
    """
    try:
        p = PackageURL.from_string(purl)
    except ValueError as e:
        raise ValueError(f"Failed to parse purl: {e}") from e

    coordinates = initialize_coordinates(p)

    handle_unexpected_qualifiers_and_version(p)

    type_handler = get_type_handler(p.type)
    if type_handler:
        coordinates = type_handler(p, coordinates)
    else:
        raise ValueError(
            f"Unsupported package type: {p.type}",
        )

    return build_coordinate_string(coordinates)


def initialize_coordinates(p: PackageURL) -> dict:
    """Initialize a dictionary holding the coordinates with basic values from the parsed PURL.

    Args:
        p (PackageURL): The parsed Package URL object.

    Returns:
        dict: A dictionary containing the basic coordinate values with keys:
            - type: Package type (empty string initially)
            - provider: Package provider (empty string initially)
            - namespace: Package namespace (- if none provided)
            - name: Package name
            - revision: Package version (empty string if none provided)
    """
    return {
        "type": "",
        "provider": "",
        "namespace": "-" if not p.namespace else p.namespace,
        "name": p.name,
        "revision": p.version if p.version else "",
    }


def handle_unexpected_qualifiers_and_version(p: PackageURL):
    """Handle some edge cases with missing or None PURL qualifiers or version.

    Args:
        p (PackageURL): The parsed Package URL object to validate and fix.
    """
    if p.qualifiers is None or isinstance(p.qualifiers, str):
        logging.warning("Unexpected qualifiers type: %s. Setting to empty dict", type(p.qualifiers))
        p.qualifiers = {}
    if p.version is None:
        logging.critical(
            "Version is None. This is required for conversion to ClearlyDefined coordinates",
        )
        sys.exit(1)

def get_type_handler(package_type: str):
    """Depending on the package type, define the function handling this package origin.

    Args:
        package_type (str): The type of package from the PURL.

    Returns:
        callable: The handler function for the specified package type, or None if unsupported.
    """
    handlers = {
        "cocoapods": handle_cocoapods,
        "cargo": handle_cargo,
        "composer": handle_composer,
        "conda": handle_conda,
        "deb": handle_deb,
        "gem": handle_gem,
        "github": handle_git,
        "gitlab": handle_git,
        "bitbucket": handle_git,
        "golang": handle_golang,
        "maven": handle_maven,
        "npm": handle_npm,
        "nuget": handle_nuget,
        "pypi": handle_pypi,
    }
    return handlers.get(package_type)


def handle_cocoapods(p: PackageURL, coordinates) -> dict:  # pylint: disable=unused-argument
    """Set type and provider for Cocoapods PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with Cocoapods-specific values:
            - type: 'pod'
            - provider: 'cocoapods'
    """
    coordinates["type"] = "pod"
    coordinates["provider"] = "cocoapods"
    return coordinates


def handle_cargo(p: PackageURL, coordinates) -> dict:  # pylint: disable=unused-argument
    """Set type and provider for Cargo PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with Cargo-specific values:
            - type: 'crate'
            - provider: 'cratesio'
    """
    coordinates["type"] = "crate"
    coordinates["provider"] = "cratesio"
    return coordinates


def handle_composer(p: PackageURL, coordinates) -> dict:  # pylint: disable=unused-argument
    """Set type and provider for Composer PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with Composer-specific values:
            - type: 'composer'
            - provider: 'packagist'
    """
    coordinates["type"] = "composer"
    coordinates["provider"] = "packagist"
    return coordinates


def handle_conda(p: PackageURL, coordinates) -> dict:
    """Set type and provider for Conda PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with Conda-specific values, or None if invalid.
            - type: 'conda'
            - provider: Based on channel qualifier ('anaconda-main', 'conda-forge', or 'anaconda-r')
            - namespace: From subdir qualifier
            - revision: Combines version with build qualifier if present

    Notes:
        Requires 'channel' and 'subdir' qualifiers in the PURL.
        Returns placeholders if channel is unsupported or subdir is missing.
    """
    coordinates["type"] = "conda"
    qualifiers = p.qualifiers or {}

    channel = qualifiers.get("channel")  # type: ignore
    if channel == "main":
        coordinates["provider"] = "anaconda-main"
    elif channel == "conda-forge":
        coordinates["provider"] = "conda-forge"
    elif channel == "anaconda-r":
        coordinates["provider"] = "anaconda-r"
    else:
        logging.error("Unsupported conda channel: %s", channel)
        coordinates["provider"] = "UNSUPPORTED_CHANNEL"

    subdir = qualifiers.get("subdir")  # type: ignore
    if not subdir:
        logging.error("Missing subdir for conda package")
        coordinates["namespace"] = "MISSING_SUBDIR"
    coordinates["namespace"] = subdir

    build = qualifiers.get("build")  # type: ignore
    if build:
        coordinates["revision"] = f"{p.version}-{build}"

    return coordinates


def handle_deb(p: PackageURL, coordinates) -> dict:
    """Set type and provider for Debian PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with Debian-specific values:
            - type: 'debsrc' for source packages, 'deb' for others
            - provider: 'debian'
            - namespace: '-'
            - revision: For binary packages, combines version with architecture
    """
    qualifiers = p.qualifiers or {}
    arch = qualifiers.get("arch")  # type: ignore

    if arch == "source":
        coordinates["type"] = "debsrc"
        coordinates["revision"] = p.version if p.version else ""
    else:
        coordinates["type"] = "deb"
        coordinates["revision"] = f"{p.version}_{arch}" if arch else p.version

    coordinates["provider"] = "debian"
    coordinates["namespace"] = "-"
    return coordinates


def handle_gem(p: PackageURL, coordinates) -> dict:  # pylint: disable=unused-argument
    """Set type and provider for Ruby Gems PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with RubyGems-specific values:
            - type: 'gem'
            - provider: 'rubygems'
    """
    coordinates["type"] = "gem"
    coordinates["provider"] = "rubygems"
    return coordinates


def handle_git(p: PackageURL, coordinates) -> dict:
    """Set type and provider for Git repository PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with Git-specific values:
            - type: 'git'
            - provider: The git host (github, gitlab, or bitbucket)
    """
    coordinates["type"] = "git"
    coordinates["provider"] = p.type
    # If the version does not look like a SHA1, it is a tag
    if not is_sha1(p.version):  # type: ignore
        coordinates["revision"] = github_tag_to_commit(
            p.namespace, p.name, p.version,  # type: ignore
        )
    return coordinates


def handle_golang(p: PackageURL, coordinates) -> dict:
    """Set type and provider for Golang PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with Golang-specific values:
            - type: 'go'
            - provider: 'golang'
            - namespace: URL-encoded namespace (/ replaced with %2f)
            - revision: Version with 'v' prefix if version exists
    """
    coordinates["type"] = "go"
    coordinates["provider"] = "golang"
    coordinates["namespace"] = coordinates["namespace"].replace("/", "%2f")
    coordinates["revision"] = f"v{p.version}" if p.version else ""
    return coordinates


def handle_maven(p: PackageURL, coordinates) -> dict:
    """Set type and provider for Maven PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with Maven-specific values:
            - type: 'maven'
            - provider: 'mavengoogle' for Android packages,
                       'gradleplugin' for Gradle plugins,
                       'mavencentral' for others
    """
    coordinates["type"] = "maven"
    if "android" in (p.namespace or ""):
        coordinates["provider"] = "mavengoogle"
    elif "gradle" in p.name.lower():
        coordinates["provider"] = "gradleplugin"
    else:
        coordinates["provider"] = "mavencentral"
    return coordinates


def handle_npm(p: PackageURL, coordinates) -> dict:  # pylint: disable=unused-argument
    """Set type and provider for NPM PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with NPM-specific values:
            - type: 'npm'
            - provider: 'npmjs'
    """
    coordinates["type"] = "npm"
    coordinates["provider"] = "npmjs"
    return coordinates


def handle_nuget(p: PackageURL, coordinates) -> dict:  # pylint: disable=unused-argument
    """Set type and provider for NuGet PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with NuGet-specific values:
            - type: 'nuget'
            - provider: 'nuget'
    """
    coordinates["type"] = "nuget"
    coordinates["provider"] = "nuget"
    return coordinates


def handle_pypi(p: PackageURL, coordinates) -> dict:  # pylint: disable=unused-argument
    """Set type and provider for PyPI PURLs.

    Args:
        p (PackageURL): The parsed Package URL object.
        coordinates (dict): The coordinate dictionary to modify.

    Returns:
        dict: The modified coordinates with PyPI-specific values:
            - type: 'pypi'
            - provider: 'pypi'
    """
    coordinates["type"] = "pypi"
    coordinates["provider"] = "pypi"
    return coordinates


def build_coordinate_string(coordinates: dict[str, str]) -> str:
    """Convert the coordinates dictionary into a ClearlyDefined coordinate string.

    Args:
        coordinates (dict[str, str]): Dictionary containing coordinate components:
            - type: Package type
            - provider: Package provider
            - namespace: Package namespace
            - name: Package name
            - revision: Package version/revision

    Returns:
        str: The formatted coordinate string.
    """
    return (
        f"{coordinates['type']}/{coordinates['provider']}/"
        f"{coordinates['namespace']}/{coordinates['name']}/{coordinates['revision']}"
    )
