"""
Copyright (C) 2016-2020 Kunal Mehta <legoktm@debian.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Optional
import base64
import functools
import json
import requests
import yaml

session = requests.Session()


def get_gerrit_file(gerrit_name: str, path: str) -> Optional[str]:
    """
    Get the contents of a file in Git repo (master branch)

    :param gerrit_name: Repository name
    :param path: File path
    :return: Contents of the file
    """
    url = 'https://gerrit.wikimedia.org/g/{}/+/master/{}?format=TEXT'.format(gerrit_name, path)
    r = session.get(url)
    if r.status_code == 404:
        return None
    return base64.b64decode(r.text).decode()


def is_bundled(repo: str) -> bool:
    """Whether a repository is bundled in the MediaWiki tarball"""
    return repo in get_bundled_list()


@functools.lru_cache()
def _settings_yaml() -> dict:
    r = session.get("https://gitlab.wikimedia.org/repos/releng/release/"
                    "-/raw/main/make-release/settings.yaml")
    r.raise_for_status()
    return yaml.safe_load(r.text)


def get_bundled_list() -> list:
    """List of repositories that are bundled in the MediaWiki tarball"""
    return [name for name in _settings_yaml()['bundles']['base']]


def get_wikimedia_deployed_list() -> list:
    """List of repositories that are Wikimedia-deployed"""
    return [name for name in _settings_yaml()['bundles']['wmf_core']]


def is_wikimedia_deployed(repo: str) -> bool:
    """Whether a repository is Wikimedia-deployed"""
    return repo in get_wikimedia_deployed_list()


def gerrit_api_request(path: str, params={}) -> dict:
    url = 'https://gerrit.wikimedia.org/r/' + path
    r = session.get(url, params=params)
    r.raise_for_status()
    return json.loads(r.text[4:])


def mw_things_repos():
    """Generator of active extension and skin repos"""
    for type_ in ['extensions', 'skins']:
        data = gerrit_api_request('projects/', params={
            'b': 'master',
            'p': 'mediawiki/%s/' % type_,
        })
        for repo in data:
            if len(repo.split('/')) != 3:
                # Subrepo
                continue
            info = data[repo]
            if info['state'] != 'ACTIVE':
                continue
            yield repo
