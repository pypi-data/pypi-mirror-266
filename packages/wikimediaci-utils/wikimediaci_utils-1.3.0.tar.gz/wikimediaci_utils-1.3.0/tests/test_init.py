"""
Copyright (C) 2016-2018 Kunal Mehta <legoktm@debian.org>

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

# These are mostly integration tests for now. Probably we want to mock API
# responses or something?

import json
import wikimediaci_utils

CITE = 'mediawiki/extensions/Cite'


def test_get_bundled_list():
    assert CITE in wikimediaci_utils.get_bundled_list()


def test_is_bundled():
    assert wikimediaci_utils.is_bundled(CITE) is True


def test_is_wikimedia_deployed():
    assert wikimediaci_utils.is_wikimedia_deployed(CITE)


def test_get_wikimedia_deployed_list():
    assert CITE in wikimediaci_utils.get_wikimedia_deployed_list()


def test_mw_things_repos():
    repos = list(wikimediaci_utils.mw_things_repos())
    assert CITE in repos
    assert 'mediawiki/extensions/DonationInterface/vendor' not in repos


def test_get_gerrit_file():
    ext_json = wikimediaci_utils.get_gerrit_file('mediawiki/extensions/Linter', 'extension.json')
    ext_info = json.loads(ext_json)
    assert ext_info['name'] == 'Linter'


def test_missing_get_gerrit_file():
    missing = wikimediaci_utils.get_gerrit_file('mediawiki/extensions/Linter', 'does_not_exist')
    assert missing is None
